import re
from pathlib import Path
from typing import Generator

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def ground_truth_opinion_date() -> pd.DataFrame:
    excel_filepath = Path("results/ground_truth_CHMP_opiniondate.xlsx")
    df = pd.read_excel(excel_filepath)
    return df


def rule_based_all() -> pd.DataFrame:
    excel_filepath = Path("results/sampled_api.xlsx")
    df = pd.read_excel(excel_filepath)
    return df


def free_text_to_date(text):
    # from free text, extract anything in the forma %Y-%m-%d
    matches = re.findall(r"\d{4}-\d{2}-\d{2}", str(text))
    if not matches:
        return ""
    dates = [
        pd.to_datetime(match, format="%Y-%m-%d") for i, match in enumerate(matches)
    ]
    # return the latest date
    return max(dates) if dates else None


def free_text_to_label(text):
    # if Not reported in text, return that
    if "not reported" in text.lower():
        return "Not reported"
    if "true" in text.lower():
        return "True"
    if "false" in text.lower():
        return "False"


def truth_and_rule_based() -> pd.DataFrame:
    ground = ground_truth_opinion_date()[["eu_pnumber", "chmp_opinion_date"]]
    rule = rule_based_all()[["eu_pnumber", "chmp_opinion_date", "eu_prime_initial"]]
    ground["eu_prime_initial"] = rule["eu_prime_initial"]
    df = pd.merge(
        ground, rule, on="eu_pnumber", how="left", suffixes=("_truth", "_rule")
    )
    # for PRIME status, the rule-based of this subset is the truth, verified
    # df["eu_prime_initial_truth"] = df["eu_prime_initial"]
    df.replace(
        "Value not reported (available for medicines authorised from 2016-03-01 onwards)",
        "Not reported",
        inplace=True,
    )
    for col in [x for x in df.columns if "date" in x]:
        df[col] = pd.to_datetime(df[col], format="%Y-%m-%d")

    return df


def add_in_random(truth_df) -> pd.DataFrame:
    # add in random dates within the range of chmp_opinion_date_truth
    truth_df["chmp_opinion_date_random"] = truth_df["chmp_opinion_date_truth"].apply(
        lambda x: x + pd.DateOffset(days=np.random.randint(-365, 365))
    )
    truth_df["eu_prime_initial_random"] = truth_df["eu_prime_initial_truth"].apply(
        lambda _: np.random.choice(["True", "False", "Not reported"])
    )
    return truth_df


def add_in_results(truth_df) -> pd.DataFrame:
    # print(list(Path("outputs/extracted").glob("*.csv")))
    for result in Path("outputs/parsed_extracted").glob("*.csv"):
        # for result in Path("outputs/extracted").glob("*.csv"):
        if result.stem.startswith("deconstructed") or "camelot" in result.stem:
            continue
        if "parsed" in result.stem:
            continue
        df = pd.read_csv(result)  # , names=["docpath", "opinion_date", "prime_status"])
        df = (
            df[["doc_path", "chmp_output", "prime_output"]]
            .rename(
                columns={
                    "chmp_output": "opinion_date",
                    "prime_output": "prime_status",
                }
            )
            .replace(
                {
                    "FALSE": "False",
                    "TRUE": "True",
                    "Value not reported (available for medicines authorised from 2016-03-01 onwards)": "Not reported",
                }
            )
        )
        # df["opinion_date"] = df["opinion_date"].apply(free_text_to_date)
        # df["prime_status"] = df["prime_status"].apply(free_text_to_label)
        df["eu_pnumber"] = df["doc_path"].apply(
            lambda x: x.split("/")[-1].split("_")[0].replace("-", "/")
        )
        df["opinion_date"] = pd.to_datetime(df["opinion_date"], format="%Y-%m-%d")
        df.rename(
            columns={
                "opinion_date": "chmp_opinion_date",
                "prime_status": "eu_prime_initial",
            },
            inplace=True,
        )
        df = df[["eu_pnumber", "chmp_opinion_date", "eu_prime_initial"]]
        tag = result.stem.replace("_extracted", "")
        df.columns = [f"{col}_{tag}" for col in df.columns]
        df.rename(columns={f"eu_pnumber_{tag}": "eu_pnumber"}, inplace=True)
        truth_df = pd.merge(
            truth_df,
            df,
            on="eu_pnumber",
            how="inner",
        )
    return truth_df


def compare_generator(df, col_basename) -> Generator:
    truth = df[f"{col_basename}_truth"]
    for col in [x for x in df.columns if col_basename in x]:
        # print(col)
        if col == f"{col_basename}_truth":
            continue
        yield col.replace(f"{col_basename}_", ""), truth, df[col]


def date_metrics(df) -> pd.DataFrame:
    metrics_df = pd.DataFrame(
        columns=[
            "input",
            "percentage_correct",
            # "mae",
            # "mse",
        ]
    )
    col_base = "chmp_opinion_date"
    for name, truth, pred in compare_generator(df, col_base):
        days_off = (pred - truth).dt.days
        metrics = {
            "input": name.replace(col_base, ""),
            "percentage_correct": np.sum(days_off == 0) / len(days_off),
            # "mae": np.mean(np.abs(days_off)),
            # "mse": np.mean(days_off**2),
        }
        metrics_df = pd.concat(
            [metrics_df, pd.DataFrame.from_dict(metrics, orient="index").T]
        )
    return metrics_df


def prime_applicable_metrics(df):
    metrics_df = pd.DataFrame([], columns=["input", "precision", "recall", "f1", "mcc"])
    col_base = "eu_prime_initial"
    for name, truth, pred in compare_generator(df, col_base):

        tp = np.sum((truth != "Not reported") & (pred != "Not reported"))
        tn = np.sum((truth == "Not reported") & (pred == "Not reported"))
        fp = np.sum((truth == "Not reported") & (pred != "Not reported"))
        fn = np.sum((truth != "Not reported") & (pred == "Not reported"))

        metrics = {
            "input": name.replace(col_base, ""),
            "precision": tp / (tp + fp),
            "recall": tp / (tp + fn),
            "f1": 2 * tp / (2 * tp + fp + fn),
            "mcc": (tp * tn - fp * fn)
            / np.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn)),
        }
        metrics_df = pd.concat(
            [metrics_df, pd.DataFrame.from_dict(metrics, orient="index").T]
        )
    return metrics_df


def prime_status_metrics(df):
    metrics_df = pd.DataFrame([], columns=["input", "precision", "recall", "f1", "mcc"])
    col_base = "eu_prime_initial"
    for name, truth, pred in compare_generator(df, col_base):
        truth = np.array(truth)
        pred = np.array(pred)
        mask = truth != "Not reported"  # only ones where status is applicable
        truth = truth[mask]
        pred = pred[mask]
        # the values are boolean strings, get the metrics and add them to the dataframe as a row with concat
        tp = np.sum((truth == "True") & (pred == "True"))
        tn = np.sum((truth == "False") & (pred == "False"))
        fp = np.sum((truth == "False") & (pred == "True"))
        fn = np.sum((truth == "True") & (pred == "False"))

        metrics = {
            "input": name.replace(col_base, ""),
            "precision": tp / (tp + fp),
            "recall": tp / (tp + fn),
            "f1": 2 * tp / (2 * tp + fp + fn),
            "mcc": (tp * tn - fp * fn)
            / np.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn)),
        }
        metrics_df = pd.concat(
            [metrics_df, pd.DataFrame.from_dict(metrics, orient="index").T]
        )
    return metrics_df


def generate_plots(df):
    Path("results").mkdir(exist_ok=True)
    metrics = {
        "date": date_metrics(df),
        "prime_applicable": prime_applicable_metrics(df),
        "prime_status": prime_status_metrics(df),
    }
    for key, value in metrics.items():
        value.to_csv(f"results/{key}_metrics.csv", index=False)
    for key, value in metrics.items():
        labels = value["input"].apply(lambda x: x.split(key)[-1])
        value.plot.bar(x="input", title=key)
        plt.savefig(f"results/{key}_metrics.png", bbox_inches="tight")


def main():
    df = truth_and_rule_based()
    # df = add_in_random(df)
    df = add_in_results(truth_and_rule_based())
    df.to_csv("results/all.csv", index=False)
    generate_plots(df)


if __name__ == "__main__":
    main()
