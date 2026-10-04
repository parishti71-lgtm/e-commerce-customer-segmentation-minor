import warnings
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    import seaborn as sns
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score
    from sklearn.preprocessing import StandardScaler
except ImportError as exc:  # pragma: no cover - environment guard
    missing_module = exc.name or "an unknown module"
    raise ImportError(
        f"Missing Python module '{missing_module}' for interpreter "
        f"'{sys.executable}'. Select this project's interpreter "
        f"({BASE_DIR / '.venv' / 'Scripts' / 'python.exe'}) in VS Code, "
        "or install requirements with that interpreter."
    ) from exc
warnings.filterwarnings("ignore")
sns.set_style("whitegrid")
sns.set_style("whitegrid")

CSV_DATASET_PATH = BASE_DIR / "Online Retail.csv"
EXCEL_DATASET_PATH = BASE_DIR / "Online Retail.xlsx"
REQUIRED_COLUMNS = {
    "InvoiceNo",
    "StockCode",
    "Description",
    "Quantity",
    "InvoiceDate",
    "UnitPrice",
    "CustomerID",
    "Country",
}


def validate_columns(df):
    missing = sorted(REQUIRED_COLUMNS - set(df.columns))
    if missing:
        raise ValueError(
            "The dataset is missing required columns: " + ", ".join(missing)
        )


def load_dataset():
    if CSV_DATASET_PATH.exists():
        df = pd.read_csv(CSV_DATASET_PATH)
    elif EXCEL_DATASET_PATH.exists():
        df = pd.read_excel(EXCEL_DATASET_PATH)
    else:
        raise FileNotFoundError(
            f"Dataset not found. Place 'Online Retail.csv' or "
            f"'Online Retail.xlsx' in {BASE_DIR}."
        )
    validate_columns(df)
    print("Dataset Shape:", df.shape)
    print(df.head())
    print(df.columns.tolist())
    print(df.info())
    print(df.isnull().sum())
    print("Duplicate Rows:", df.duplicated().sum())
    print(df.describe())
    return df


def preprocess_data(df):
    df = df.copy().drop_duplicates()
    validate_columns(df)

    df = df.dropna(subset=["CustomerID", "InvoiceDate", "Quantity", "UnitPrice"])
    df["CustomerID"] = pd.to_numeric(df["CustomerID"], errors="coerce")
    df = df.dropna(subset=["CustomerID"]).copy()
    df["CustomerID"] = df["CustomerID"].astype(int)

    df["InvoiceNo"] = df["InvoiceNo"].astype(str)
    df = df[~df["InvoiceNo"].str.startswith("C")].copy()
    df["InvoiceNo"] = df["InvoiceNo"].astype(str)

    df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")
    df["UnitPrice"] = pd.to_numeric(df["UnitPrice"], errors="coerce")
    df = df.dropna(subset=["Quantity", "UnitPrice"]).copy()

    df = df[df["Quantity"] > 0]
    df = df[df["UnitPrice"] > 0]
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce")
    df = df.dropna(subset=["InvoiceDate"]).copy()
    df["TotalAmount"] = df["Quantity"] * df["UnitPrice"]
    print("Dataset Shape After Cleaning:", df.shape)
    print(df[["Quantity", "UnitPrice", "TotalAmount"]].head())
    return df


def build_rfm(df):
    analysis_date = df["InvoiceDate"].max() + pd.Timedelta(days=1)

    recency = df.groupby("CustomerID").agg({
        "InvoiceDate": lambda x: (analysis_date - x.max()).days
    })
    recency.columns = ["Recency"]

    frequency = df.groupby("CustomerID").agg({
        "InvoiceNo": "nunique"
    })
    frequency.columns = ["Frequency"]

    monetary = df.groupby("CustomerID").agg({
        "TotalAmount": "sum"
    })
    monetary.columns = ["Monetary"]

    rfm = pd.concat([recency, frequency, monetary], axis=1)
    print(rfm.head())
    print(rfm.describe())
    return rfm


def plot_country_distribution(df):
    country_counts = df["Country"].value_counts().head(10)
    plt.figure(figsize=(10, 6))
    sns.barplot(x=country_counts.values, y=country_counts.index, palette="viridis")
    plt.title("Top 10 Countries by Number of Transactions")
    plt.xlabel("Number of Transactions")
    plt.ylabel("Country")
    plt.tight_layout()
    plt.show()


def plot_monthly_sales(df):
    df["Month"] = df["InvoiceDate"].dt.to_period("M")
    monthly_sales = df.groupby("Month")["TotalAmount"].sum()
    plt.figure(figsize=(14, 6))
    plt.plot(monthly_sales.index.astype(str), monthly_sales.values, marker="o", color="blue")
    plt.title("Monthly Sales")
    plt.xlabel("Month")
    plt.ylabel("Revenue")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def plot_rfm_distributions(rfm):
    plt.figure(figsize=(15, 5))

    plt.subplot(1, 3, 1)
    sns.histplot(rfm["Recency"], bins=30, kde=True, color="blue")
    plt.title("Recency Distribution")

    plt.subplot(1, 3, 2)
    sns.histplot(rfm["Frequency"], bins=30, kde=True, color="green")
    plt.title("Frequency Distribution")

    plt.subplot(1, 3, 3)
    sns.histplot(rfm["Monetary"], bins=30, kde=True, color="orange")
    plt.title("Monetary Distribution")

    plt.tight_layout()
    plt.show()

    plt.figure(figsize=(15, 5))

    plt.subplot(1, 3, 1)
    sns.boxplot(y=rfm["Recency"], color="skyblue")
    plt.title("Recency Outliers")

    plt.subplot(1, 3, 2)
    sns.boxplot(y=rfm["Frequency"], color="lightgreen")
    plt.title("Frequency Outliers")

    plt.subplot(1, 3, 3)
    sns.boxplot(y=rfm["Monetary"], color="orange")
    plt.title("Monetary Outliers")

    plt.tight_layout()
    plt.show()


def build_clusters(rfm):
    rfm_log = rfm.copy()
    rfm_log["Recency"] = np.log1p(rfm_log["Recency"])
    rfm_log["Frequency"] = np.log1p(rfm_log["Frequency"])
    rfm_log["Monetary"] = np.log1p(rfm_log["Monetary"])

    scaler = StandardScaler()
    rfm_scaled_array = scaler.fit_transform(rfm_log)
    rfm_scaled = pd.DataFrame(
        rfm_scaled_array,
        columns=["Recency", "Frequency", "Monetary"],
        index=rfm.index,
    )

    inertia = []
    k_values = range(2, 11)
    for k in k_values:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(rfm_scaled)
        inertia.append(kmeans.inertia_)

    plt.figure(figsize=(10, 6))
    plt.plot(k_values, inertia, marker="o", linewidth=2, color="blue")
    plt.title("Elbow Method for Optimal Number of Clusters")
    plt.xlabel("Number of Clusters")
    plt.ylabel("Inertia")
    plt.xticks(k_values)
    plt.grid(True)
    plt.show()

    optimal_k = 4
    kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
    rfm["Cluster"] = kmeans.fit_predict(rfm_scaled)

    cluster_counts = rfm["Cluster"].value_counts().sort_index()
    print(cluster_counts)

    plt.figure(figsize=(8, 5))
    sns.barplot(x=cluster_counts.index, y=cluster_counts.values, palette="Set2")
    plt.title("Number of Customers in Each Cluster")
    plt.xlabel("Cluster")
    plt.ylabel("Number of Customers")
    plt.show()

    cluster_summary = rfm.groupby("Cluster").agg({
        "Recency": "mean",
        "Frequency": "mean",
        "Monetary": "mean",
    }).round(2)
    cluster_summary["CustomerCount"] = rfm.groupby("Cluster").size()
    print(cluster_summary)

    silhouette_avg = silhouette_score(rfm_scaled, rfm["Cluster"])
    print("Silhouette Score:", round(silhouette_avg, 4))

    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=rfm, x="Frequency", y="Monetary", hue="Cluster", palette="Set1", s=100)
    plt.title("Customer Segmentation: Frequency vs Monetary")
    plt.xlabel("Frequency")
    plt.ylabel("Monetary Value")
    plt.show()

    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=rfm, x="Recency", y="Monetary", hue="Cluster", palette="Set2", s=100)
    plt.title("Customer Segmentation: Recency vs Monetary")
    plt.xlabel("Recency")
    plt.ylabel("Monetary Value")
    plt.show()

    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=rfm, x="Recency", y="Frequency", hue="Cluster", palette="Set1", s=100)
    plt.title("Customer Segmentation: Recency vs Frequency")
    plt.xlabel("Recency")
    plt.ylabel("Frequency")
    plt.show()

    return rfm, cluster_summary, silhouette_avg


def assign_segments(cluster_summary, rfm):
    cluster_summary["BusinessScore"] = (
        cluster_summary["Frequency"].rank()
        + cluster_summary["Monetary"].rank()
        - cluster_summary["Recency"].rank()
    )

    vip_cluster = cluster_summary["BusinessScore"].idxmax()
    at_risk_cluster = cluster_summary["Recency"].idxmax()

    remaining_clusters = [c for c in cluster_summary.index if c not in [vip_cluster, at_risk_cluster]]

    if len(remaining_clusters) > 0:
        loyal_cluster = cluster_summary.loc[remaining_clusters, "Frequency"].idxmax()
    else:
        loyal_cluster = vip_cluster

    potential_clusters = [
        c for c in cluster_summary.index if c not in [vip_cluster, at_risk_cluster, loyal_cluster]
    ]

    cluster_names = {
        vip_cluster: "VIP Customers",
        at_risk_cluster: "At-Risk Customers",
        loyal_cluster: "Loyal Customers",
    }

    for cluster_id in potential_clusters:
        cluster_names[cluster_id] = "Potential Customers"

    rfm["Segment"] = rfm["Cluster"].map(cluster_names)
    final_report = rfm.groupby("Segment").agg(
        Customers=("Segment", "count"),
        Avg_Recency=("Recency", "mean"),
        Avg_Frequency=("Frequency", "mean"),
        Avg_Monetary=("Monetary", "mean"),
    ).round(2)

    print(final_report)
    return rfm, final_report


def plot_segment_summary(rfm, final_report):
    segment_counts = rfm["Segment"].value_counts()

    plt.figure(figsize=(10, 6))
    plt.pie(segment_counts.values, labels=segment_counts.index, autopct="%1.1f%%", startangle=90)
    plt.title("Customer Segment Distribution")
    plt.show()

    plt.figure(figsize=(10, 6))
    sns.barplot(x=segment_counts.index, y=segment_counts.values, palette="Set2")
    plt.title("Number of Customers by Segment")
    plt.xlabel("Customer Segment")
    plt.ylabel("Number of Customers")
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.show()

    plt.figure(figsize=(15, 5))
    plt.subplot(1, 3, 1)
    sns.barplot(data=rfm, x="Segment", y="Recency", palette="Set1")
    plt.title("Average Recency")
    plt.xticks(rotation=30)

    plt.subplot(1, 3, 2)
    sns.barplot(data=rfm, x="Segment", y="Frequency", palette="Set2")
    plt.title("Average Frequency")
    plt.xticks(rotation=30)

    plt.subplot(1, 3, 3)
    sns.barplot(data=rfm, x="Segment", y="Monetary", palette="Set3")
    plt.title("Average Monetary Value")
    plt.xticks(rotation=30)

    plt.tight_layout()
    plt.show()

    print(final_report)
    return segment_counts


def print_customer_highlights(rfm):
    top_customers = rfm.sort_values(by="Monetary", ascending=False).head(10)
    print("Top 10 Customers by Spending:")
    print(top_customers)

    frequent_customers = rfm.sort_values(by="Frequency", ascending=False).head(10)
    print("Top 10 Most Frequent Customers:")
    print(frequent_customers)

    at_risk_customers = rfm.sort_values(by="Recency", ascending=False).head(20)
    print("At-Risk Customers:")
    print(at_risk_customers)


def print_recommendations(final_report):
    recommendations = {
        "VIP Customers": "Provide exclusive discounts, loyalty rewards, premium support and early access to new products.",
        "Loyal Customers": "Offer loyalty points, personalized recommendations and special member offers.",
        "Potential Customers": "Use targeted discounts, product recommendations and promotional campaigns to increase purchase frequency.",
        "At-Risk Customers": "Send win-back emails, personalized offers and limited-time discounts to encourage repeat purchases.",
    }

    for segment in final_report.index:
        print(f"\n{segment}:")
        print(recommendations.get(segment, "Create a personalized marketing strategy."))


def main():
    df = load_dataset()
    df = preprocess_data(df)
    number_of_customers = df["CustomerID"].nunique()
    number_of_orders = df["InvoiceNo"].nunique()
    total_revenue = df["TotalAmount"].sum()
    print("Number of Customers:", number_of_customers)
    print("Number of Orders:", number_of_orders)
    print("Total Revenue:", round(total_revenue, 2))

    plot_country_distribution(df)
    plot_monthly_sales(df)

    rfm = build_rfm(df)
    plot_rfm_distributions(rfm)
    rfm, cluster_summary, silhouette_avg = build_clusters(rfm)
    rfm, final_report = assign_segments(cluster_summary, rfm)
    segment_counts = plot_segment_summary(rfm, final_report)
    print_customer_highlights(rfm)
    print_recommendations(final_report)

    rfm.to_csv(BASE_DIR / "customer_segments.csv", index=True)
    final_report.to_csv(BASE_DIR / "customer_segment_summary.csv")

    print("\nFiles saved:")
    print("customer_segments.csv")
    print("customer_segment_summary.csv")

    print("\nPROJECT SUMMARY")
    print("Total Customers:", number_of_customers)
    print("Total Orders:", number_of_orders)
    print("Total Revenue:", round(total_revenue, 2))
    print("Number of Clusters:", 4)
    print("Silhouette Score:", round(silhouette_avg, 4))

    print("\nCustomer Segments:")
    for segment, count in segment_counts.items():
        print(f"{segment}: {count} customers")

    print("\nE-COMMERCE CUSTOMER SEGMENTATION COMPLETED!")


if __name__ == "__main__":
    main()
