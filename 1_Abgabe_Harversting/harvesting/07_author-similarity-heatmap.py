import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def build_matrix(df: pd.DataFrame) -> pd.DataFrame:
    df = df[["Author A", "Author B", "Similarity"]].copy()

    matrix = df.pivot_table(
        index="Author A",
        columns="Author B",
        values="Similarity",
        aggfunc="mean",
    )

    matrix = matrix.combine_first(matrix.T)
    all_ids = sorted(set(matrix.index) | set(matrix.columns))
    matrix = matrix.reindex(index=all_ids, columns=all_ids)
    for i in range(len(matrix)):
        matrix.iat[i, i] = 1.0
    return matrix.fillna(0.0)


def draw_heatmap(matrix: pd.DataFrame, output: str) -> None:
    n = len(matrix)
    cell = max(0.55, min(1.1, 11 / max(1, n)))
    plt.figure(figsize=(n * cell + 2.5, n * cell + 1.8))

    sns.heatmap(
        matrix,
        cmap="OrRd",
        vmin=0.0,
        vmax=1.0,
        annot=True,
        fmt=".2f",
        linewidths=0.5,
        linecolor="white",
        square=True,
        cbar_kws={"label": "Ähnlichkeit", "shrink": 0.8},
    )

    plt.title("Ähnlichkeitsmatrix der Autoren", fontsize=12, pad=12)
    plt.xticks(rotation=60, ha="right")
    plt.yticks(rotation=0)
    plt.xlabel("")
    plt.ylabel("")
    plt.tight_layout()
    plt.savefig(output, dpi=300, bbox_inches="tight")
    plt.close()


if __name__ == "__main__":
    input_file = "author-similarity_otsuka-ochiai.csv"
    df = pd.read_csv(input_file, names=["Author A", "Author B", "Similarity"])
    matrix = build_matrix(df)
    draw_heatmap(matrix, "author-similarity_otsuka-ochiai.png")
