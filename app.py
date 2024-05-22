import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO

# Load the dataset
@st.cache_data
def load_data(file_path):
    return pd.read_csv(file_path)

# Custom palette for plots
brand_colors = ["#F36E2C", "#01895C", "#035539", "#B74106"]

# Load Declined Consent dataset
declined_consent = pd.read_excel('Declined Consent.xlsx')

# Function to plot pie chart
def plot_pie_chart(df):
    if 'DeclineReasonId' in df.columns:
        decline_reason_counts = df['DeclineReasonId'].value_counts()
        plt.figure(figsize=(12, 16), facecolor='white')
        wedges, texts, autotexts = plt.pie(
            decline_reason_counts, labels=decline_reason_counts.index, autopct='%1.1f%%',
            startangle=140, colors=brand_colors[:len(decline_reason_counts)]
        )
        plt.setp(autotexts, size=10, color="black")
        plt.setp(texts, size=12)
        plt.legend(wedges, [f'{label} ({count})' for label, count in zip(decline_reason_counts.index, decline_reason_counts)],
                   title="Decline Reasons", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
        plt.title('Distribution of Declined Reasons')
        plt.axis('equal')
        st.pyplot(plt)
        return plt
    else:
        st.error("Column 'DeclineReasonId' does not exist in the dataset.")

# Function to plot heatmap
def plot_heatmap(df):
    if 'LocationName' in df.columns and 'DeclineReasonId' in df.columns:
        pivot_table = df.pivot_table(index='LocationName', columns='DeclineReasonId', aggfunc='size', fill_value=0)
        plt.figure(figsize=(18, 16))
        sns.heatmap(pivot_table, annot=True, fmt="d", cmap=sns.color_palette(brand_colors, as_cmap=True), cbar_kws={'label': 'Count'})
        plt.title('Heatmap of Decline Consent Counts for Each Location')
        plt.xlabel('Decline Consent')
        plt.ylabel('Location')
        plt.xticks(rotation=90)
        st.pyplot(plt)
        return plt
    else:
        st.error("Required columns do not exist in the dataset.")

# Function to plot bar chart of DeclineReasonId for each LocationName
def plot_bar_chart_location(df):
    if 'LocationName' in df.columns and 'DeclineReasonId' in df.columns:
        pivot_table = df.pivot_table(index='LocationName', columns='DeclineReasonId', aggfunc='size', fill_value=0)
        plt.figure(figsize=(14, 8))
        pivot_table.plot(kind='bar', stacked=True, figsize=(14, 8), color=brand_colors[:len(pivot_table.columns)])
        plt.title('Count of Each DeclineReasonId for Each LocationName')
        plt.xlabel('LocationName')
        plt.ylabel('Count')
        plt.legend(title='DeclineReasonId')
        plt.xticks(rotation=90)
        st.pyplot(plt)
        return plt
    else:
        st.error("Required columns do not exist in the dataset.")

# Function to plot bar chart of DeclineReasonId counts for each DistrictName
def plot_bar_chart_district(df):
    if 'DistrictName' in df.columns and 'DeclineReasonId' in df.columns:
        district_decline_counts = df.groupby('DistrictName')['DeclineReasonId'].count().reset_index()
        district_decline_counts.columns = ['DistrictName', 'DeclineReasonId_Count']
        plt.figure(figsize=(18, 12))
        sns.set(style="whitegrid")
        bar_plot = sns.barplot(x='DistrictName', y='DeclineReasonId_Count', data=district_decline_counts, palette=brand_colors)
        bar_plot.set_title('Distribution of DeclineReasonId Counts for Each Sub County', fontsize=16)
        bar_plot.set_xlabel('Sub County', fontsize=14)
        bar_plot.set_ylabel('Declined Consent', fontsize=14)
        bar_plot.set_xticklabels(bar_plot.get_xticklabels(), rotation=45, horizontalalignment='right', fontsize=12)
        for p in bar_plot.patches:
            bar_plot.annotate(format(p.get_height(), '.0f'), 
                              (p.get_x() + p.get_width() / 2., p.get_height()), 
                              ha='center', va='center', 
                              xytext=(0, 9), 
                              textcoords='offset points',
                              fontsize=10)
        st.pyplot(plt)
        return plt
    else:
        st.error("Required columns do not exist in the dataset.")

# Function to plot bar chart for Change by Sub County
def plot_change_by_sub_county(df, title):
    if 'DistrictName' in df.columns:
        if 'Total' in df.columns:
            try:
                df['Total'] = df['Total'].str.rstrip('%').astype('float') / 100.0
            except AttributeError:
                # The 'Total' column is already numeric
                pass
            plt.figure(figsize=(18, 12))
            sns.set(style="whitegrid")
            bar_plot = sns.barplot(x='DistrictName', y='Total', data=df, palette=brand_colors)
            bar_plot.set_title(title, fontsize=16)
            bar_plot.set_xlabel('Sub County', fontsize=14)
            bar_plot.set_ylabel('Percentage', fontsize=14)
            bar_plot.set_xticklabels(bar_plot.get_xticklabels(), rotation=45, horizontalalignment='right', fontsize=12)
            for p in bar_plot.patches:
                bar_plot.annotate(format(p.get_height() * 100, '.1f') + '%', 
                                  (p.get_x() + p.get_width() / 2., p.get_height()), 
                                  ha='center', va='center', 
                                  xytext=(0, 9), 
                                  textcoords='offset points',
                                  fontsize=10)
            st.pyplot(plt)
            return plt
        else:
            st.error("Column 'Total' does not exist in the dataset.")
    else:
        st.error("Column 'DistrictName' does not exist in the dataset.")

# Function to plot bar chart for Change by Location
def plot_change_by_location(df, title):
    if 'LocationName' in df.columns:
        df = df[df['LocationName'] != 'Total']  # Remove 'Total' row
        df.set_index('LocationName').plot(kind='bar', stacked=True, figsize=(18, 12), color=brand_colors)
        plt.title(title, fontsize=16)
        plt.xlabel('Location', fontsize=14)
        plt.ylabel('Count', fontsize=14)
        plt.xticks(rotation=45, horizontalalignment='right', fontsize=12)
        plt.legend(title='Status')
        st.pyplot(plt)
        return plt
    else:
        st.error("Column 'LocationName' does not exist in the dataset.")

# Function to plot bar chart for Values
def plot_values_distribution(df, title, variable_name):
    if variable_name in df.columns:
        df.set_index(variable_name)[['First_visit', 'Second_visit']].plot(kind='bar', figsize=(18, 12), color=brand_colors[:2])
        plt.title(title, fontsize=16)
        plt.xlabel(variable_name, fontsize=14)
        plt.ylabel('Values', fontsize=14)
        plt.xticks(rotation=45, horizontalalignment='right', fontsize=12)
        plt.legend(title='Visit')
        st.pyplot(plt)
        return plt
    else:
        st.error(f"Column '{variable_name}' does not exist in the dataset.")

# Function to create a download link for the plots
def get_image_download_link(fig, filename, text):
    buf = BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    st.download_button(label=text, data=buf, file_name=filename, mime="image/png")

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select Page", ["About", "Visualization"])

if page == "About":
    st.title("About This Project")
    st.write("""
        Third Party Quality Assurance for Phase II for Households' Registration Under the Enhanced Single Registry for the Kenya Social Inclusion Project(KSEIP)

        **KISII COUNTY TPQA ANALYSIS REPORT**
        
        - **Visualize** the data with interactive plots.
        - **Analyze** descriptive statistics.
    """)

elif page == "Visualization":
    st.title("Data Visualization")
    st.subheader("Select Dataset")

    # Define datasets
    datasets = [
        "Declined Consent", "Floor Mismatch", "Roof Mismatch", "Lighting Mismatch",
        "Habitable Rooms Mismatch", "Cooking Fuel Mismatch", "Waste Disposal Mismatch",
        "Water Source Mismatch", "Wall Mismatch",
        "Head DOB", "Head Education", "Head ID", "Member Names", "Orphans",
        "Relationship Head", "Size", "Spouse DOB", "Spouse Education", "Spouse ID", "Summary"
    ]

    # Split datasets into two columns
    col1, col2 = st.columns(2)
    selected_datasets = []

    with col1:
        for dataset in datasets[:10]:
            if st.checkbox(dataset):
                selected_datasets.append(dataset)

    with col2:
        for dataset in datasets[10:]:
            if st.checkbox(dataset):
                selected_datasets.append(dataset)

    # Display the selected dataset
    if len(selected_datasets) == 1:
        selected_dataset = selected_datasets[0]

        if selected_dataset == "Declined Consent":
            st.write("## Declined Consent Dataset Visualizations")

            # Checkboxes for selecting plot types
            col1, col2, col3 = st.columns(3)
            with col1:
                show_pie_chart = st.checkbox("Pie Chart")
                show_heatmap = st.checkbox("Heatmap")
            with col2:
                show_bar_plot_location = st.checkbox("Location Bar Chart")
                show_stacked_bar_plot = st.checkbox("Sub County Bar Chart")

            if show_pie_chart:
                st.write("### Pie Chart of Declined Reasons")
                pie_chart = plot_pie_chart(declined_consent)
                if pie_chart:
                    get_image_download_link(pie_chart, "pie_chart.png", "Download Pie Chart")

            if show_heatmap:
                st.write("### Heatmap of Decline Consent Counts for Each Location")
                heatmap = plot_heatmap(declined_consent)
                if heatmap:
                    get_image_download_link(heatmap, "heatmap.png", "Download Heatmap")

            if show_bar_plot_location:
                st.write("### Bar Chart of Decline Reasons by Location")
                bar_chart_location = plot_bar_chart_location(declined_consent)
                if bar_chart_location:
                    get_image_download_link(bar_chart_location, "bar_chart_location.png", "Download Bar Chart")

            if show_stacked_bar_plot:
                st.write("### Bar Chart of Decline Reasons by Sub County")
                bar_chart_district = plot_bar_chart_district(declined_consent)
                if bar_chart_district:
                    get_image_download_link(bar_chart_district, "bar_chart_district.png", "Download Bar Chart")

        else:
            file_mapping = {
                "Floor Mismatch": ("floordistrict.csv", "floorlocation.csv", "floorvalues.csv", "Floor.x"),
                "Roof Mismatch": ("roofdistrict.csv", "rooflocation.csv", "roofvalues.csv", "Roof.x"),
                "Lighting Mismatch": ("lightdistrict.csv", "lightlocation.csv", "lightvalues.csv", "LightingFuel.x"),
                "Habitable Rooms Mismatch": ("roomdistrict.csv", "roomslocation.csv"),
                "Cooking Fuel Mismatch": ("cookingdistrict.csv", "cookinglocation.csv", "cookingvalues.csv", "CookingFuel.x"),
                "Waste Disposal Mismatch": ("toiletdistrict.csv", "toiletlocation.csv", "toiletvalues.csv", "HumanWasteDisposal.x"),
                "Water Source Mismatch": ("waterdistrict.csv", "waterlocation.csv", "watervalues.csv", "WaterSource.x"),
                "Wall Mismatch": ("walldistrict.csv", "wall location.csv", "wallvalues.csv", "Wall.x"),
                "Head DOB": ("headdobdistrict.csv", "headdoblocation.csv"),
                "Head Education": ("headedudistrict.csv", "headedulocation.csv"),
                "Head ID": ("headiddistrict.csv", "headidlocation.csv"),
                "Member Names": ("membernamesdistrict.csv", "membernameslocation.csv"),
                "Orphans": ("opharndistrict.csv", "opharnlocation.csv"),
                "Relationship Head": ("relatioshipheaddistrict.csv", "relatioshipheadlocation.csv"),
                "Size": ("sizedistrict.csv", "sizelocation.csv"),
                "Spouse DOB": ("spousedobdistrict.csv", "spousedoblocation.csv"),
                "Spouse Education": ("spouseedudistrict.csv", "spouseedulocation.csv"),
                "Spouse ID": ("spouseiddistrict.csv", "spouseidlocation.csv"),
                "Summary": ("summary.csv",)
            }

            files = file_mapping[selected_dataset]

            # Load datasets
            district_df = load_data(files[0])
            location_df = load_data(files[1]) if len(files) > 1 else None
            values_df = None
            variable_name = None

            if len(files) > 2:
                values_file = files[2]
                variable_name = files[3]
                values_df = load_data(values_file)

            st.write(f"## {selected_dataset} Dataset Visualizations")

            # Checkboxes for selecting plot types
            col1, col2, col3 = st.columns(3)
            with col1:
                show_district_bar_chart = st.checkbox(f"{selected_dataset} by Sub County")
                if location_df is not None:
                    show_location_bar_chart = st.checkbox(f"{selected_dataset} by Location")
            with col2:
                if values_df is not None:
                    show_values_distribution = st.checkbox(f"{selected_dataset} Frequencies")

            if show_district_bar_chart:
                st.write(f"### {selected_dataset} by Sub County")
                change_by_sub_county_chart = plot_change_by_sub_county(district_df, f"{selected_dataset} by Sub County")
                if change_by_sub_county_chart:
                    get_image_download_link(change_by_sub_county_chart, f"{selected_dataset}_by_sub_county.png", "Download Chart")

            if location_df is not None and show_location_bar_chart:
                st.write(f"### {selected_dataset} by Location")
                change_by_location_chart = plot_change_by_location(location_df, f"{selected_dataset} by Location")
                if change_by_location_chart:
                    get_image_download_link(change_by_location_chart, f"{selected_dataset}_by_location.png", "Download Chart")

            if values_df is not None and show_values_distribution:
                st.write(f"### {selected_dataset} Frequencies")
                values_distribution_chart = plot_values_distribution(values_df, f"{selected_dataset} Frequencies", variable_name)
                if values_distribution_chart:
                    get_image_download_link(values_distribution_chart, f"{selected_dataset}Frequencies.png", "Download Chart")

    elif len(selected_datasets) > 1:
        st.error("Please select only one dataset at a time.")
    else:
        st.info("Please select a variable from the options above.")

