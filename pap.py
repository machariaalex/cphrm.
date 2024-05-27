# Importing necessary libraries
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

# Function to plot bar chart for Values with values on top of bars
def plot_values_distribution(df, title, variable_name):
    if variable_name in df.columns:
        ax = df.set_index(variable_name)[['First_visit', 'Second_visit']].plot(kind='bar', figsize=(18, 12), color=brand_colors[:2])
        plt.title(title, fontsize=16)
        plt.xlabel(variable_name, fontsize=14)
        plt.ylabel('Values', fontsize=14)
        plt.xticks(rotation=45, horizontalalignment='right', fontsize=12)
        plt.legend(title='Visit')
        
        # Display values on top of bars
        for p in ax.patches:
            ax.annotate(f'{int(p.get_height())}', (p.get_x() + p.get_width() / 2., p.get_height()), ha='center', va='center', xytext=(0, 10), textcoords='offset points', fontsize=10)
        
        plt.tight_layout()
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

# Function to plot summary dataset with values on top of bars
def plot_summary(df):
    plt.figure(figsize=(10, 8))
    ax = sns.barplot(x=df['HH Variable'], y=df['Percentage'].astype(int), palette=brand_colors)
    plt.title('Summary of HH Variables', fontsize=16)
    plt.xlabel('HH Variables', fontsize=14)
    plt.ylabel('Mismatch %', fontsize=14)
    plt.xticks(rotation=85)
    
    # Display values on top of bars
    for p in ax.patches:
        ax.annotate(f'{int(p.get_height())}%', (p.get_x() + p.get_width() / 2., p.get_height()), ha='center', va='center', xytext=(0, 10), textcoords='offset points', fontsize=10)
    
    plt.tight_layout()
    st.pyplot(plt)
    return plt




# Landing Page
# def landing_page():
#     st.title("Project Details")
#     st.write("""
#         The primary objective of this task was to check variances for the Kisii dataset between the original data
#         and recollected data, focusing on several key variables related to household characteristics. The tasks
#         included data cleaning, analysis, visualization, providing a usable Python script for system integration,
#         and offering recommendations for implementing AI/ML to enhance future analyses.
#     """)

# Sidebar for navigation
st.sidebar.title("Navigation")

# Add dropdown button for County
county_option = st.sidebar.selectbox("Select County", ["Kisii", "Laikipia", "Migori", "Kisumu", "Lamu", "Kilifi", "Kwale", "Murang'a", "Narok", "Tharaka Nithi", "Tana River", "Isiolo","Garissa","Taita Taveta","West Pokot", "Baringo", "Samburu", "Kitui"])

# Depending on the selected County, show appropriate options
if county_option == "Kisii":
    # landing_page()  # Show landing page

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
        # st.title("Data Visualization")
        st.write("### Select a variable")

        # Define datasets
        datasets = [
            "Declined Consent", "Floor", "Roof", "Lighting",
            "Habitable Rooms", "Cooking Fuel", "Waste Disposal",
            "Water Source", "Wall",
            "Household Head DOB", "Household Head Education", "Household Head ID", "Household Member Names", "Orphans",
            "Relationship to Head", "Household Size", "Spouse DOB", "Spouse Education", "Spouse ID", "Kisii County Summary"
        ]

        # Split datasets into two columns
        col1, col2 = st.columns(2)
        selected_datasets = []

        with col1:
            for dataset in datasets[:10]:
                if dataset != "Kisii County Summary":
                    if st.checkbox(dataset):
                        selected_datasets.append(dataset)

        with col2:
            for dataset in datasets[10:]:
                if st.checkbox(dataset):
                    selected_datasets.append(dataset)

        # Display the selected dataset
        if "Kisii County Summary" in selected_datasets:
            st.write("###Total Variable Mismmatch in Kisii County")

            summary_data = {
                "HH Variable": [
                    "HH Head ID Number", "HH Head Date of Birth", "Spouse ID Number", "Spouse Date of Birth",
                    "Household Size", "Household member names", "Education Levels of HH Head", "Education levels of Spouse",
                    "Orphan members", "Relationships to household head", "Number of main rooms", "Floor", "Wall", "Roof",
                    "Source of Water", "Source of Lighting", "Toilet type", "Cooking fuel", "Any Disabled"
                ],
                "Percentage": [3.6, 7.5, 10.6, 6.3, 9.9, 0.0, 54.1, 53.6, 57.6, 55.8, 57.1, 15.5, 22.3, 12.2, 57.7, 47.7, 48.1, 5.8,0.0]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_plot = plot_summary(summary_df,)

        elif len(selected_datasets) == 1:
            selected_dataset = selected_datasets[0]

            if selected_dataset == "Declined Consent":
                st.write("### Declined Consent Dataset Visualizations")

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
                    "Kisii County Summary": ("kisii_summary.csv",),
                    "Floor": ("floordistrict.csv", "floorlocation.csv", "floorvalues.csv", "Floor.x"),
                    "Roof": ("roofdistrict.csv", "rooflocation.csv", "roofvalues.csv", "Roof.x"),
                    "Lighting": ("lightingdistrict.csv", "lightinglocation.csv", "lightingvalues.csv", "LightingFuel.x"),
                    "Habitable Rooms": ("roomsdistrict.csv", "roomslocation.csv"),
                    "Cooking Fuel": ("cookingdistrict.csv", "cookinglocation.csv", "cookingvalues.csv", "CookingFuel.x"),
                    "Waste Disposal": ("toilet district.csv", "toiletlocation.csv", "toiletvalues.csv", "HumanWasteDisposal.x"),
                    "Water Source": ("waterdistrict.csv", "waterlocation.csv", "watervalues.csv", "WaterSource.x"),
                    "Wall": ("walldistrict.csv", "wall location.csv", "wallvalues.csv", "Wall.x"),
                    "Household Head DOB": ("headdobdistrict.csv", "headdoblocation.csv"),
                    "Household Head Education": ("headedudistrict.csv", "headedulocation.csv"),
                    "Household Head ID": ("headiddistrict.csv", "headidlocation.csv"),
                    "Household Member Names": ("namesdistrict.csv", "membernameslocation.csv"),
                    "Orphans": ("opharndistrict.csv", "opharnlocation.csv"),
                    "Relationship to Head": ("relatioshipheaddistrict.csv", "relatioshipheadlocation.csv"),
                    "Household Size": ("sizedistrict.csv", "sizelocation.csv"),
                    "Spouse DOB": ("spousedobdistrict.csv", "spousedoblocation.csv"),
                    "Spouse Education": ("spouseedudistrict.csv", "spouseedulocation.csv"),
                    "Spouse ID": ("spouseiddistrict.csv", "spouseidlocation.csv"),
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

                st.write(f"#### {selected_dataset} Dataset Visualizations")

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


elif county_option == "Laikipia":

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
        # st.title("Data Visualization")
        st.write("### Select a variable")

        # Define datasets
        datasets = [
            "Declined Consent", "Floor", "Roof", "Lighting",
            "Habitable Rooms", "Cooking Fuel", "Waste Disposal",
            "Water Source", "Wall",
            "Household Head DOB", "Household Head Education", "Household Head ID", "Household Member Names", "Orphans",
            "Relationship to Head", "Household Size", "Spouse DOB", "Spouse Education", "Spouse ID", "Kisii County Summary"
        ]

        # Split datasets into two columns
        col1, col2 = st.columns(2)
        selected_datasets = []

        with col1:
            for dataset in datasets[:10]:
                if dataset != "Kisii County Summary":
                    if st.checkbox(dataset):
                        selected_datasets.append(dataset)

        with col2:
            for dataset in datasets[10:]:
                if st.checkbox(dataset):
                    selected_datasets.append(dataset)

        # Display the selected dataset
        if "Kisii County Summary" in selected_datasets:
            st.write("###Total Variable Mismmatch in Kisii County")

            summary_data = {
                "HH Variable": [
                    "HH Head ID Number", "HH Head Date of Birth", "Spouse ID Number", "Spouse Date of Birth",
                    "Household Size", "Household member names", "Education Levels of HH Head", "Education levels of Spouse",
                    "Orphan members", "Relationships to household head", "Number of main rooms", "Floor", "Wall", "Roof",
                    "Source of Water", "Source of Lighting", "Toilet type", "Cooking fuel", "Any Disabled"
                ],
                "Percentage": [3.6, 7.5, 10.6, 6.3, 9.9, 0.0, 54.1, 53.6, 57.6, 55.8, 57.1, 15.5, 22.3, 12.2, 57.7, 47.7, 48.1, 5.8,0.0]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_plot = plot_summary(summary_df,)

        elif len(selected_datasets) == 1:
            selected_dataset = selected_datasets[0]

            if selected_dataset == "Declined Consent":
                st.write("### Declined Consent Dataset Visualizations")

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
                    "Kisii County Summary": ("kisii_summary.csv",),
                    "Floor": ("floordistrict.csv", "floorlocation.csv", "floorvalues.csv", "Floor.x"),
                    "Roof": ("roofdistrict.csv", "rooflocation.csv", "roofvalues.csv", "Roof.x"),
                    "Lighting": ("lightingdistrict.csv", "lightinglocation.csv", "lightingvalues.csv", "LightingFuel.x"),
                    "Habitable Rooms": ("roomsdistrict.csv", "roomslocation.csv"),
                    "Cooking Fuel": ("cookingdistrict.csv", "cookinglocation.csv", "cookingvalues.csv", "CookingFuel.x"),
                    "Waste Disposal": ("toilet district.csv", "toiletlocation.csv", "toiletvalues.csv", "HumanWasteDisposal.x"),
                    "Water Source": ("waterdistrict.csv", "waterlocation.csv", "watervalues.csv", "WaterSource.x"),
                    "Wall": ("walldistrict.csv", "wall location.csv", "wallvalues.csv", "Wall.x"),
                    "Household Head DOB": ("headdobdistrict.csv", "headdoblocation.csv"),
                    "Household Head Education": ("headedudistrict.csv", "headedulocation.csv"),
                    "Household Head ID": ("headiddistrict.csv", "headidlocation.csv"),
                    "Household Member Names": ("namesdistrict.csv", "membernameslocation.csv"),
                    "Orphans": ("opharndistrict.csv", "opharnlocation.csv"),
                    "Relationship to Head": ("relatioshipheaddistrict.csv", "relatioshipheadlocation.csv"),
                    "Household Size": ("sizedistrict.csv", "sizelocation.csv"),
                    "Spouse DOB": ("spousedobdistrict.csv", "spousedoblocation.csv"),
                    "Spouse Education": ("spouseedudistrict.csv", "spouseedulocation.csv"),
                    "Spouse ID": ("spouseiddistrict.csv", "spouseidlocation.csv"),
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

                st.write(f"#### {selected_dataset} Dataset Visualizations")

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

elif county_option == "Migori":
    # landing_page()  # Show landing page

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
        # st.title("Data Visualization")
        st.write("### Select a variable")

        # Define datasets
        datasets = [
            "Declined Consent", "Floor", "Roof", "Lighting",
            "Habitable Rooms", "Cooking Fuel", "Waste Disposal",
            "Water Source", "Wall",
            "Household Head DOB", "Household Head Education", "Household Head ID", "Household Member Names", "Orphans",
            "Relationship to Head", "Household Size", "Spouse DOB", "Spouse Education", "Spouse ID", "Kisii County Summary"
        ]

        # Split datasets into two columns
        col1, col2 = st.columns(2)
        selected_datasets = []

        with col1:
            for dataset in datasets[:10]:
                if dataset != "Kisii County Summary":
                    if st.checkbox(dataset):
                        selected_datasets.append(dataset)

        with col2:
            for dataset in datasets[10:]:
                if st.checkbox(dataset):
                    selected_datasets.append(dataset)

        # Display the selected dataset
        if "Kisii County Summary" in selected_datasets:
            st.write("###Total Variable Mismmatch in Kisii County")

            summary_data = {
                "HH Variable": [
                    "HH Head ID Number", "HH Head Date of Birth", "Spouse ID Number", "Spouse Date of Birth",
                    "Household Size", "Household member names", "Education Levels of HH Head", "Education levels of Spouse",
                    "Orphan members", "Relationships to household head", "Number of main rooms", "Floor", "Wall", "Roof",
                    "Source of Water", "Source of Lighting", "Toilet type", "Cooking fuel", "Any Disabled"
                ],
                "Percentage": [3.6, 7.5, 10.6, 6.3, 9.9, 0.0, 54.1, 53.6, 57.6, 55.8, 57.1, 15.5, 22.3, 12.2, 57.7, 47.7, 48.1, 5.8,0.0]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_plot = plot_summary(summary_df,)

        elif len(selected_datasets) == 1:
            selected_dataset = selected_datasets[0]

            if selected_dataset == "Declined Consent":
                st.write("### Declined Consent Dataset Visualizations")

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
                    "Kisii County Summary": ("kisii_summary.csv",),
                    "Floor": ("floordistrict.csv", "floorlocation.csv", "floorvalues.csv", "Floor.x"),
                    "Roof": ("roofdistrict.csv", "rooflocation.csv", "roofvalues.csv", "Roof.x"),
                    "Lighting": ("lightingdistrict.csv", "lightinglocation.csv", "lightingvalues.csv", "LightingFuel.x"),
                    "Habitable Rooms": ("roomsdistrict.csv", "roomslocation.csv"),
                    "Cooking Fuel": ("cookingdistrict.csv", "cookinglocation.csv", "cookingvalues.csv", "CookingFuel.x"),
                    "Waste Disposal": ("toilet district.csv", "toiletlocation.csv", "toiletvalues.csv", "HumanWasteDisposal.x"),
                    "Water Source": ("waterdistrict.csv", "waterlocation.csv", "watervalues.csv", "WaterSource.x"),
                    "Wall": ("walldistrict.csv", "wall location.csv", "wallvalues.csv", "Wall.x"),
                    "Household Head DOB": ("headdobdistrict.csv", "headdoblocation.csv"),
                    "Household Head Education": ("headedudistrict.csv", "headedulocation.csv"),
                    "Household Head ID": ("headiddistrict.csv", "headidlocation.csv"),
                    "Household Member Names": ("namesdistrict.csv", "membernameslocation.csv"),
                    "Orphans": ("opharndistrict.csv", "opharnlocation.csv"),
                    "Relationship to Head": ("relatioshipheaddistrict.csv", "relatioshipheadlocation.csv"),
                    "Household Size": ("sizedistrict.csv", "sizelocation.csv"),
                    "Spouse DOB": ("spousedobdistrict.csv", "spousedoblocation.csv"),
                    "Spouse Education": ("spouseedudistrict.csv", "spouseedulocation.csv"),
                    "Spouse ID": ("spouseiddistrict.csv", "spouseidlocation.csv"),
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

                st.write(f"#### {selected_dataset} Dataset Visualizations")

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


elif county_option == "Kisumu":
    # landing_page()  # Show landing page

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
        # st.title("Data Visualization")
        st.write("### Select a variable")

        # Define datasets
        datasets = [
            "Declined Consent", "Floor", "Roof", "Lighting",
            "Habitable Rooms", "Cooking Fuel", "Waste Disposal",
            "Water Source", "Wall",
            "Household Head DOB", "Household Head Education", "Household Head ID", "Household Member Names", "Orphans",
            "Relationship to Head", "Household Size", "Spouse DOB", "Spouse Education", "Spouse ID", "Kisii County Summary"
        ]

        # Split datasets into two columns
        col1, col2 = st.columns(2)
        selected_datasets = []

        with col1:
            for dataset in datasets[:10]:
                if dataset != "Kisii County Summary":
                    if st.checkbox(dataset):
                        selected_datasets.append(dataset)

        with col2:
            for dataset in datasets[10:]:
                if st.checkbox(dataset):
                    selected_datasets.append(dataset)

        # Display the selected dataset
        if "Kisii County Summary" in selected_datasets:
            st.write("###Total Variable Mismmatch in Kisii County")

            summary_data = {
                "HH Variable": [
                    "HH Head ID Number", "HH Head Date of Birth", "Spouse ID Number", "Spouse Date of Birth",
                    "Household Size", "Household member names", "Education Levels of HH Head", "Education levels of Spouse",
                    "Orphan members", "Relationships to household head", "Number of main rooms", "Floor", "Wall", "Roof",
                    "Source of Water", "Source of Lighting", "Toilet type", "Cooking fuel", "Any Disabled"
                ],
                "Percentage": [3.6, 7.5, 10.6, 6.3, 9.9, 0.0, 54.1, 53.6, 57.6, 55.8, 57.1, 15.5, 22.3, 12.2, 57.7, 47.7, 48.1, 5.8,0.0]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_plot = plot_summary(summary_df,)

        elif len(selected_datasets) == 1:
            selected_dataset = selected_datasets[0]

            if selected_dataset == "Declined Consent":
                st.write("### Declined Consent Dataset Visualizations")

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
                    "Kisii County Summary": ("kisii_summary.csv",),
                    "Floor": ("floordistrict.csv", "floorlocation.csv", "floorvalues.csv", "Floor.x"),
                    "Roof": ("roofdistrict.csv", "rooflocation.csv", "roofvalues.csv", "Roof.x"),
                    "Lighting": ("lightingdistrict.csv", "lightinglocation.csv", "lightingvalues.csv", "LightingFuel.x"),
                    "Habitable Rooms": ("roomsdistrict.csv", "roomslocation.csv"),
                    "Cooking Fuel": ("cookingdistrict.csv", "cookinglocation.csv", "cookingvalues.csv", "CookingFuel.x"),
                    "Waste Disposal": ("toilet district.csv", "toiletlocation.csv", "toiletvalues.csv", "HumanWasteDisposal.x"),
                    "Water Source": ("waterdistrict.csv", "waterlocation.csv", "watervalues.csv", "WaterSource.x"),
                    "Wall": ("walldistrict.csv", "wall location.csv", "wallvalues.csv", "Wall.x"),
                    "Household Head DOB": ("headdobdistrict.csv", "headdoblocation.csv"),
                    "Household Head Education": ("headedudistrict.csv", "headedulocation.csv"),
                    "Household Head ID": ("headiddistrict.csv", "headidlocation.csv"),
                    "Household Member Names": ("namesdistrict.csv", "membernameslocation.csv"),
                    "Orphans": ("opharndistrict.csv", "opharnlocation.csv"),
                    "Relationship to Head": ("relatioshipheaddistrict.csv", "relatioshipheadlocation.csv"),
                    "Household Size": ("sizedistrict.csv", "sizelocation.csv"),
                    "Spouse DOB": ("spousedobdistrict.csv", "spousedoblocation.csv"),
                    "Spouse Education": ("spouseedudistrict.csv", "spouseedulocation.csv"),
                    "Spouse ID": ("spouseiddistrict.csv", "spouseidlocation.csv"),
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

                st.write(f"#### {selected_dataset} Dataset Visualizations")

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

elif county_option == "Muranga":
    # landing_page()  # Show landing page

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
        # st.title("Data Visualization")
        st.write("### Select a variable")

        # Define datasets
        datasets = [
            "Declined Consent", "Floor", "Roof", "Lighting",
            "Habitable Rooms", "Cooking Fuel", "Waste Disposal",
            "Water Source", "Wall",
            "Household Head DOB", "Household Head Education", "Household Head ID", "Household Member Names", "Orphans",
            "Relationship to Head", "Household Size", "Spouse DOB", "Spouse Education", "Spouse ID", "Kisii County Summary"
        ]

        # Split datasets into two columns
        col1, col2 = st.columns(2)
        selected_datasets = []

        with col1:
            for dataset in datasets[:10]:
                if dataset != "Kisii County Summary":
                    if st.checkbox(dataset):
                        selected_datasets.append(dataset)

        with col2:
            for dataset in datasets[10:]:
                if st.checkbox(dataset):
                    selected_datasets.append(dataset)

        # Display the selected dataset
        if "Kisii County Summary" in selected_datasets:
            st.write("###Total Variable Mismmatch in Kisii County")

            summary_data = {
                "HH Variable": [
                    "HH Head ID Number", "HH Head Date of Birth", "Spouse ID Number", "Spouse Date of Birth",
                    "Household Size", "Household member names", "Education Levels of HH Head", "Education levels of Spouse",
                    "Orphan members", "Relationships to household head", "Number of main rooms", "Floor", "Wall", "Roof",
                    "Source of Water", "Source of Lighting", "Toilet type", "Cooking fuel", "Any Disabled"
                ],
                "Percentage": [3.6, 7.5, 10.6, 6.3, 9.9, 0.0, 54.1, 53.6, 57.6, 55.8, 57.1, 15.5, 22.3, 12.2, 57.7, 47.7, 48.1, 5.8,0.0]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_plot = plot_summary(summary_df,)

        elif len(selected_datasets) == 1:
            selected_dataset = selected_datasets[0]

            if selected_dataset == "Declined Consent":
                st.write("### Declined Consent Dataset Visualizations")

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
                    "Kisii County Summary": ("kisii_summary.csv",),
                    "Floor": ("floordistrict.csv", "floorlocation.csv", "floorvalues.csv", "Floor.x"),
                    "Roof": ("roofdistrict.csv", "rooflocation.csv", "roofvalues.csv", "Roof.x"),
                    "Lighting": ("lightingdistrict.csv", "lightinglocation.csv", "lightingvalues.csv", "LightingFuel.x"),
                    "Habitable Rooms": ("roomsdistrict.csv", "roomslocation.csv"),
                    "Cooking Fuel": ("cookingdistrict.csv", "cookinglocation.csv", "cookingvalues.csv", "CookingFuel.x"),
                    "Waste Disposal": ("toilet district.csv", "toiletlocation.csv", "toiletvalues.csv", "HumanWasteDisposal.x"),
                    "Water Source": ("waterdistrict.csv", "waterlocation.csv", "watervalues.csv", "WaterSource.x"),
                    "Wall": ("walldistrict.csv", "wall location.csv", "wallvalues.csv", "Wall.x"),
                    "Household Head DOB": ("headdobdistrict.csv", "headdoblocation.csv"),
                    "Household Head Education": ("headedudistrict.csv", "headedulocation.csv"),
                    "Household Head ID": ("headiddistrict.csv", "headidlocation.csv"),
                    "Household Member Names": ("namesdistrict.csv", "membernameslocation.csv"),
                    "Orphans": ("opharndistrict.csv", "opharnlocation.csv"),
                    "Relationship to Head": ("relatioshipheaddistrict.csv", "relatioshipheadlocation.csv"),
                    "Household Size": ("sizedistrict.csv", "sizelocation.csv"),
                    "Spouse DOB": ("spousedobdistrict.csv", "spousedoblocation.csv"),
                    "Spouse Education": ("spouseedudistrict.csv", "spouseedulocation.csv"),
                    "Spouse ID": ("spouseiddistrict.csv", "spouseidlocation.csv"),
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

                st.write(f"#### {selected_dataset} Dataset Visualizations")

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




elif county_option == "Tana River":
    # landing_page()  # Show landing page

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
        # st.title("Data Visualization")
        st.write("### Select a variable")

        # Define datasets
        datasets = [
            "Declined Consent", "Floor", "Roof", "Lighting",
            "Habitable Rooms", "Cooking Fuel", "Waste Disposal",
            "Water Source", "Wall",
            "Household Head DOB", "Household Head Education", "Household Head ID", "Household Member Names", "Orphans",
            "Relationship to Head", "Household Size", "Spouse DOB", "Spouse Education", "Spouse ID", "Kisii County Summary"
        ]

        # Split datasets into two columns
        col1, col2 = st.columns(2)
        selected_datasets = []

        with col1:
            for dataset in datasets[:10]:
                if dataset != "Kisii County Summary":
                    if st.checkbox(dataset):
                        selected_datasets.append(dataset)

        with col2:
            for dataset in datasets[10:]:
                if st.checkbox(dataset):
                    selected_datasets.append(dataset)

        # Display the selected dataset
        if "Kisii County Summary" in selected_datasets:
            st.write("###Total Variable Mismmatch in Kisii County")

            summary_data = {
                "HH Variable": [
                    "HH Head ID Number", "HH Head Date of Birth", "Spouse ID Number", "Spouse Date of Birth",
                    "Household Size", "Household member names", "Education Levels of HH Head", "Education levels of Spouse",
                    "Orphan members", "Relationships to household head", "Number of main rooms", "Floor", "Wall", "Roof",
                    "Source of Water", "Source of Lighting", "Toilet type", "Cooking fuel", "Any Disabled"
                ],
                "Percentage": [3.6, 7.5, 10.6, 6.3, 9.9, 0.0, 54.1, 53.6, 57.6, 55.8, 57.1, 15.5, 22.3, 12.2, 57.7, 47.7, 48.1, 5.8,0.0]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_plot = plot_summary(summary_df,)

        elif len(selected_datasets) == 1:
            selected_dataset = selected_datasets[0]

            if selected_dataset == "Declined Consent":
                st.write("### Declined Consent Dataset Visualizations")

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
                    "Kisii County Summary": ("kisii_summary.csv",),
                    "Floor": ("floordistrict.csv", "floorlocation.csv", "floorvalues.csv", "Floor.x"),
                    "Roof": ("roofdistrict.csv", "rooflocation.csv", "roofvalues.csv", "Roof.x"),
                    "Lighting": ("lightingdistrict.csv", "lightinglocation.csv", "lightingvalues.csv", "LightingFuel.x"),
                    "Habitable Rooms": ("roomsdistrict.csv", "roomslocation.csv"),
                    "Cooking Fuel": ("cookingdistrict.csv", "cookinglocation.csv", "cookingvalues.csv", "CookingFuel.x"),
                    "Waste Disposal": ("toilet district.csv", "toiletlocation.csv", "toiletvalues.csv", "HumanWasteDisposal.x"),
                    "Water Source": ("waterdistrict.csv", "waterlocation.csv", "watervalues.csv", "WaterSource.x"),
                    "Wall": ("walldistrict.csv", "wall location.csv", "wallvalues.csv", "Wall.x"),
                    "Household Head DOB": ("headdobdistrict.csv", "headdoblocation.csv"),
                    "Household Head Education": ("headedudistrict.csv", "headedulocation.csv"),
                    "Household Head ID": ("headiddistrict.csv", "headidlocation.csv"),
                    "Household Member Names": ("namesdistrict.csv", "membernameslocation.csv"),
                    "Orphans": ("opharndistrict.csv", "opharnlocation.csv"),
                    "Relationship to Head": ("relatioshipheaddistrict.csv", "relatioshipheadlocation.csv"),
                    "Household Size": ("sizedistrict.csv", "sizelocation.csv"),
                    "Spouse DOB": ("spousedobdistrict.csv", "spousedoblocation.csv"),
                    "Spouse Education": ("spouseedudistrict.csv", "spouseedulocation.csv"),
                    "Spouse ID": ("spouseiddistrict.csv", "spouseidlocation.csv"),
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

                st.write(f"#### {selected_dataset} Dataset Visualizations")

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



elif county_option == "Taita Taveta":
    # landing_page()  # Show landing page

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
        # st.title("Data Visualization")
        st.write("### Select a variable")

        # Define datasets
        datasets = [
            "Declined Consent", "Floor", "Roof", "Lighting",
            "Habitable Rooms", "Cooking Fuel", "Waste Disposal",
            "Water Source", "Wall",
            "Household Head DOB", "Household Head Education", "Household Head ID", "Household Member Names", "Orphans",
            "Relationship to Head", "Household Size", "Spouse DOB", "Spouse Education", "Spouse ID", "Kisii County Summary"
        ]

        # Split datasets into two columns
        col1, col2 = st.columns(2)
        selected_datasets = []

        with col1:
            for dataset in datasets[:10]:
                if dataset != "Kisii County Summary":
                    if st.checkbox(dataset):
                        selected_datasets.append(dataset)

        with col2:
            for dataset in datasets[10:]:
                if st.checkbox(dataset):
                    selected_datasets.append(dataset)

        # Display the selected dataset
        if "Kisii County Summary" in selected_datasets:
            st.write("###Total Variable Mismmatch in Kisii County")

            summary_data = {
                "HH Variable": [
                    "HH Head ID Number", "HH Head Date of Birth", "Spouse ID Number", "Spouse Date of Birth",
                    "Household Size", "Household member names", "Education Levels of HH Head", "Education levels of Spouse",
                    "Orphan members", "Relationships to household head", "Number of main rooms", "Floor", "Wall", "Roof",
                    "Source of Water", "Source of Lighting", "Toilet type", "Cooking fuel", "Any Disabled"
                ],
                "Percentage": [3.6, 7.5, 10.6, 6.3, 9.9, 0.0, 54.1, 53.6, 57.6, 55.8, 57.1, 15.5, 22.3, 12.2, 57.7, 47.7, 48.1, 5.8,0.0]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_plot = plot_summary(summary_df,)

        elif len(selected_datasets) == 1:
            selected_dataset = selected_datasets[0]

            if selected_dataset == "Declined Consent":
                st.write("### Declined Consent Dataset Visualizations")

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
                    "Kisii County Summary": ("kisii_summary.csv",),
                    "Floor": ("floordistrict.csv", "floorlocation.csv", "floorvalues.csv", "Floor.x"),
                    "Roof": ("roofdistrict.csv", "rooflocation.csv", "roofvalues.csv", "Roof.x"),
                    "Lighting": ("lightingdistrict.csv", "lightinglocation.csv", "lightingvalues.csv", "LightingFuel.x"),
                    "Habitable Rooms": ("roomsdistrict.csv", "roomslocation.csv"),
                    "Cooking Fuel": ("cookingdistrict.csv", "cookinglocation.csv", "cookingvalues.csv", "CookingFuel.x"),
                    "Waste Disposal": ("toilet district.csv", "toiletlocation.csv", "toiletvalues.csv", "HumanWasteDisposal.x"),
                    "Water Source": ("waterdistrict.csv", "waterlocation.csv", "watervalues.csv", "WaterSource.x"),
                    "Wall": ("walldistrict.csv", "wall location.csv", "wallvalues.csv", "Wall.x"),
                    "Household Head DOB": ("headdobdistrict.csv", "headdoblocation.csv"),
                    "Household Head Education": ("headedudistrict.csv", "headedulocation.csv"),
                    "Household Head ID": ("headiddistrict.csv", "headidlocation.csv"),
                    "Household Member Names": ("namesdistrict.csv", "membernameslocation.csv"),
                    "Orphans": ("opharndistrict.csv", "opharnlocation.csv"),
                    "Relationship to Head": ("relatioshipheaddistrict.csv", "relatioshipheadlocation.csv"),
                    "Household Size": ("sizedistrict.csv", "sizelocation.csv"),
                    "Spouse DOB": ("spousedobdistrict.csv", "spousedoblocation.csv"),
                    "Spouse Education": ("spouseedudistrict.csv", "spouseedulocation.csv"),
                    "Spouse ID": ("spouseiddistrict.csv", "spouseidlocation.csv"),
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

                st.write(f"#### {selected_dataset} Dataset Visualizations")

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

elif county_option == "Tharaka Nithi":
    # landing_page()  # Show landing page

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
        # st.title("Data Visualization")
        st.write("### Select a variable")

        # Define datasets
        datasets = [
            "Declined Consent", "Floor", "Roof", "Lighting",
            "Habitable Rooms", "Cooking Fuel", "Waste Disposal",
            "Water Source", "Wall",
            "Household Head DOB", "Household Head Education", "Household Head ID", "Household Member Names", "Orphans",
            "Relationship to Head", "Household Size", "Spouse DOB", "Spouse Education", "Spouse ID", "Kisii County Summary"
        ]

        # Split datasets into two columns
        col1, col2 = st.columns(2)
        selected_datasets = []

        with col1:
            for dataset in datasets[:10]:
                if dataset != "Kisii County Summary":
                    if st.checkbox(dataset):
                        selected_datasets.append(dataset)

        with col2:
            for dataset in datasets[10:]:
                if st.checkbox(dataset):
                    selected_datasets.append(dataset)

        # Display the selected dataset
        if "Kisii County Summary" in selected_datasets:
            st.write("###Total Variable Mismmatch in Kisii County")

            summary_data = {
                "HH Variable": [
                    "HH Head ID Number", "HH Head Date of Birth", "Spouse ID Number", "Spouse Date of Birth",
                    "Household Size", "Household member names", "Education Levels of HH Head", "Education levels of Spouse",
                    "Orphan members", "Relationships to household head", "Number of main rooms", "Floor", "Wall", "Roof",
                    "Source of Water", "Source of Lighting", "Toilet type", "Cooking fuel", "Any Disabled"
                ],
                "Percentage": [3.6, 7.5, 10.6, 6.3, 9.9, 0.0, 54.1, 53.6, 57.6, 55.8, 57.1, 15.5, 22.3, 12.2, 57.7, 47.7, 48.1, 5.8,0.0]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_plot = plot_summary(summary_df,)

        elif len(selected_datasets) == 1:
            selected_dataset = selected_datasets[0]

            if selected_dataset == "Declined Consent":
                st.write("### Declined Consent Dataset Visualizations")

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
                    "Kisii County Summary": ("kisii_summary.csv",),
                    "Floor": ("floordistrict.csv", "floorlocation.csv", "floorvalues.csv", "Floor.x"),
                    "Roof": ("roofdistrict.csv", "rooflocation.csv", "roofvalues.csv", "Roof.x"),
                    "Lighting": ("lightingdistrict.csv", "lightinglocation.csv", "lightingvalues.csv", "LightingFuel.x"),
                    "Habitable Rooms": ("roomsdistrict.csv", "roomslocation.csv"),
                    "Cooking Fuel": ("cookingdistrict.csv", "cookinglocation.csv", "cookingvalues.csv", "CookingFuel.x"),
                    "Waste Disposal": ("toilet district.csv", "toiletlocation.csv", "toiletvalues.csv", "HumanWasteDisposal.x"),
                    "Water Source": ("waterdistrict.csv", "waterlocation.csv", "watervalues.csv", "WaterSource.x"),
                    "Wall": ("walldistrict.csv", "wall location.csv", "wallvalues.csv", "Wall.x"),
                    "Household Head DOB": ("headdobdistrict.csv", "headdoblocation.csv"),
                    "Household Head Education": ("headedudistrict.csv", "headedulocation.csv"),
                    "Household Head ID": ("headiddistrict.csv", "headidlocation.csv"),
                    "Household Member Names": ("namesdistrict.csv", "membernameslocation.csv"),
                    "Orphans": ("opharndistrict.csv", "opharnlocation.csv"),
                    "Relationship to Head": ("relatioshipheaddistrict.csv", "relatioshipheadlocation.csv"),
                    "Household Size": ("sizedistrict.csv", "sizelocation.csv"),
                    "Spouse DOB": ("spousedobdistrict.csv", "spousedoblocation.csv"),
                    "Spouse Education": ("spouseedudistrict.csv", "spouseedulocation.csv"),
                    "Spouse ID": ("spouseiddistrict.csv", "spouseidlocation.csv"),
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

                st.write(f"#### {selected_dataset} Dataset Visualizations")

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


elif county_option == "Garissa":
    # landing_page()  # Show landing page

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
        # st.title("Data Visualization")
        st.write("### Select a variable")

        # Define datasets
        datasets = [
            "Declined Consent", "Floor", "Roof", "Lighting",
            "Habitable Rooms", "Cooking Fuel", "Waste Disposal",
            "Water Source", "Wall",
            "Household Head DOB", "Household Head Education", "Household Head ID", "Household Member Names", "Orphans",
            "Relationship to Head", "Household Size", "Spouse DOB", "Spouse Education", "Spouse ID", "Kisii County Summary"
        ]

        # Split datasets into two columns
        col1, col2 = st.columns(2)
        selected_datasets = []

        with col1:
            for dataset in datasets[:10]:
                if dataset != "Kisii County Summary":
                    if st.checkbox(dataset):
                        selected_datasets.append(dataset)

        with col2:
            for dataset in datasets[10:]:
                if st.checkbox(dataset):
                    selected_datasets.append(dataset)

        # Display the selected dataset
        if "Kisii County Summary" in selected_datasets:
            st.write("###Total Variable Mismmatch in Kisii County")

            summary_data = {
                "HH Variable": [
                    "HH Head ID Number", "HH Head Date of Birth", "Spouse ID Number", "Spouse Date of Birth",
                    "Household Size", "Household member names", "Education Levels of HH Head", "Education levels of Spouse",
                    "Orphan members", "Relationships to household head", "Number of main rooms", "Floor", "Wall", "Roof",
                    "Source of Water", "Source of Lighting", "Toilet type", "Cooking fuel", "Any Disabled"
                ],
                "Percentage": [3.6, 7.5, 10.6, 6.3, 9.9, 0.0, 54.1, 53.6, 57.6, 55.8, 57.1, 15.5, 22.3, 12.2, 57.7, 47.7, 48.1, 5.8,0.0]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_plot = plot_summary(summary_df,)

        elif len(selected_datasets) == 1:
            selected_dataset = selected_datasets[0]

            if selected_dataset == "Declined Consent":
                st.write("### Declined Consent Dataset Visualizations")

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
                    "Kisii County Summary": ("kisii_summary.csv",),
                    "Floor": ("floordistrict.csv", "floorlocation.csv", "floorvalues.csv", "Floor.x"),
                    "Roof": ("roofdistrict.csv", "rooflocation.csv", "roofvalues.csv", "Roof.x"),
                    "Lighting": ("lightingdistrict.csv", "lightinglocation.csv", "lightingvalues.csv", "LightingFuel.x"),
                    "Habitable Rooms": ("roomsdistrict.csv", "roomslocation.csv"),
                    "Cooking Fuel": ("cookingdistrict.csv", "cookinglocation.csv", "cookingvalues.csv", "CookingFuel.x"),
                    "Waste Disposal": ("toilet district.csv", "toiletlocation.csv", "toiletvalues.csv", "HumanWasteDisposal.x"),
                    "Water Source": ("waterdistrict.csv", "waterlocation.csv", "watervalues.csv", "WaterSource.x"),
                    "Wall": ("walldistrict.csv", "wall location.csv", "wallvalues.csv", "Wall.x"),
                    "Household Head DOB": ("headdobdistrict.csv", "headdoblocation.csv"),
                    "Household Head Education": ("headedudistrict.csv", "headedulocation.csv"),
                    "Household Head ID": ("headiddistrict.csv", "headidlocation.csv"),
                    "Household Member Names": ("namesdistrict.csv", "membernameslocation.csv"),
                    "Orphans": ("opharndistrict.csv", "opharnlocation.csv"),
                    "Relationship to Head": ("relatioshipheaddistrict.csv", "relatioshipheadlocation.csv"),
                    "Household Size": ("sizedistrict.csv", "sizelocation.csv"),
                    "Spouse DOB": ("spousedobdistrict.csv", "spousedoblocation.csv"),
                    "Spouse Education": ("spouseedudistrict.csv", "spouseedulocation.csv"),
                    "Spouse ID": ("spouseiddistrict.csv", "spouseidlocation.csv"),
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

                st.write(f"#### {selected_dataset} Dataset Visualizations")

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

elif county_option == "Kilifi":
    # landing_page()  # Show landing page

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
        # st.title("Data Visualization")
        st.write("### Select a variable")

        # Define datasets
        datasets = [
            "Declined Consent", "Floor", "Roof", "Lighting",
            "Habitable Rooms", "Cooking Fuel", "Waste Disposal",
            "Water Source", "Wall",
            "Household Head DOB", "Household Head Education", "Household Head ID", "Household Member Names", "Orphans",
            "Relationship to Head", "Household Size", "Spouse DOB", "Spouse Education", "Spouse ID", "Kisii County Summary"
        ]

        # Split datasets into two columns
        col1, col2 = st.columns(2)
        selected_datasets = []

        with col1:
            for dataset in datasets[:10]:
                if dataset != "Kisii County Summary":
                    if st.checkbox(dataset):
                        selected_datasets.append(dataset)

        with col2:
            for dataset in datasets[10:]:
                if st.checkbox(dataset):
                    selected_datasets.append(dataset)

        # Display the selected dataset
        if "Kisii County Summary" in selected_datasets:
            st.write("###Total Variable Mismmatch in Kisii County")

            summary_data = {
                "HH Variable": [
                    "HH Head ID Number", "HH Head Date of Birth", "Spouse ID Number", "Spouse Date of Birth",
                    "Household Size", "Household member names", "Education Levels of HH Head", "Education levels of Spouse",
                    "Orphan members", "Relationships to household head", "Number of main rooms", "Floor", "Wall", "Roof",
                    "Source of Water", "Source of Lighting", "Toilet type", "Cooking fuel", "Any Disabled"
                ],
                "Percentage": [3.6, 7.5, 10.6, 6.3, 9.9, 0.0, 54.1, 53.6, 57.6, 55.8, 57.1, 15.5, 22.3, 12.2, 57.7, 47.7, 48.1, 5.8,0.0]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_plot = plot_summary(summary_df,)

        elif len(selected_datasets) == 1:
            selected_dataset = selected_datasets[0]

            if selected_dataset == "Declined Consent":
                st.write("### Declined Consent Dataset Visualizations")

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
                    "Kisii County Summary": ("kisii_summary.csv",),
                    "Floor": ("floordistrict.csv", "floorlocation.csv", "floorvalues.csv", "Floor.x"),
                    "Roof": ("roofdistrict.csv", "rooflocation.csv", "roofvalues.csv", "Roof.x"),
                    "Lighting": ("lightingdistrict.csv", "lightinglocation.csv", "lightingvalues.csv", "LightingFuel.x"),
                    "Habitable Rooms": ("roomsdistrict.csv", "roomslocation.csv"),
                    "Cooking Fuel": ("cookingdistrict.csv", "cookinglocation.csv", "cookingvalues.csv", "CookingFuel.x"),
                    "Waste Disposal": ("toilet district.csv", "toiletlocation.csv", "toiletvalues.csv", "HumanWasteDisposal.x"),
                    "Water Source": ("waterdistrict.csv", "waterlocation.csv", "watervalues.csv", "WaterSource.x"),
                    "Wall": ("walldistrict.csv", "wall location.csv", "wallvalues.csv", "Wall.x"),
                    "Household Head DOB": ("headdobdistrict.csv", "headdoblocation.csv"),
                    "Household Head Education": ("headedudistrict.csv", "headedulocation.csv"),
                    "Household Head ID": ("headiddistrict.csv", "headidlocation.csv"),
                    "Household Member Names": ("namesdistrict.csv", "membernameslocation.csv"),
                    "Orphans": ("opharndistrict.csv", "opharnlocation.csv"),
                    "Relationship to Head": ("relatioshipheaddistrict.csv", "relatioshipheadlocation.csv"),
                    "Household Size": ("sizedistrict.csv", "sizelocation.csv"),
                    "Spouse DOB": ("spousedobdistrict.csv", "spousedoblocation.csv"),
                    "Spouse Education": ("spouseedudistrict.csv", "spouseedulocation.csv"),
                    "Spouse ID": ("spouseiddistrict.csv", "spouseidlocation.csv"),
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

                st.write(f"#### {selected_dataset} Dataset Visualizations")

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
                

elif county_option == "Kitui":
    # landing_page()  # Show landing page

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
        # st.title("Data Visualization")
        st.write("### Select a variable")

        # Define datasets
        datasets = [
            "Declined Consent", "Floor", "Roof", "Lighting",
            "Habitable Rooms", "Cooking Fuel", "Waste Disposal",
            "Water Source", "Wall",
            "Household Head DOB", "Household Head Education", "Household Head ID", "Household Member Names", "Orphans",
            "Relationship to Head", "Household Size", "Spouse DOB", "Spouse Education", "Spouse ID", "Kisii County Summary"
        ]

        # Split datasets into two columns
        col1, col2 = st.columns(2)
        selected_datasets = []

        with col1:
            for dataset in datasets[:10]:
                if dataset != "Kisii County Summary":
                    if st.checkbox(dataset):
                        selected_datasets.append(dataset)

        with col2:
            for dataset in datasets[10:]:
                if st.checkbox(dataset):
                    selected_datasets.append(dataset)

        # Display the selected dataset
        if "Kisii County Summary" in selected_datasets:
            st.write("###Total Variable Mismmatch in Kisii County")

            summary_data = {
                "HH Variable": [
                    "HH Head ID Number", "HH Head Date of Birth", "Spouse ID Number", "Spouse Date of Birth",
                    "Household Size", "Household member names", "Education Levels of HH Head", "Education levels of Spouse",
                    "Orphan members", "Relationships to household head", "Number of main rooms", "Floor", "Wall", "Roof",
                    "Source of Water", "Source of Lighting", "Toilet type", "Cooking fuel", "Any Disabled"
                ],
                "Percentage": [3.6, 7.5, 10.6, 6.3, 9.9, 0.0, 54.1, 53.6, 57.6, 55.8, 57.1, 15.5, 22.3, 12.2, 57.7, 47.7, 48.1, 5.8,0.0]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_plot = plot_summary(summary_df,)

        elif len(selected_datasets) == 1:
            selected_dataset = selected_datasets[0]

            if selected_dataset == "Declined Consent":
                st.write("### Declined Consent Dataset Visualizations")

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
                    "Kisii County Summary": ("kisii_summary.csv",),
                    "Floor": ("floordistrict.csv", "floorlocation.csv", "floorvalues.csv", "Floor.x"),
                    "Roof": ("roofdistrict.csv", "rooflocation.csv", "roofvalues.csv", "Roof.x"),
                    "Lighting": ("lightingdistrict.csv", "lightinglocation.csv", "lightingvalues.csv", "LightingFuel.x"),
                    "Habitable Rooms": ("roomsdistrict.csv", "roomslocation.csv"),
                    "Cooking Fuel": ("cookingdistrict.csv", "cookinglocation.csv", "cookingvalues.csv", "CookingFuel.x"),
                    "Waste Disposal": ("toilet district.csv", "toiletlocation.csv", "toiletvalues.csv", "HumanWasteDisposal.x"),
                    "Water Source": ("waterdistrict.csv", "waterlocation.csv", "watervalues.csv", "WaterSource.x"),
                    "Wall": ("walldistrict.csv", "wall location.csv", "wallvalues.csv", "Wall.x"),
                    "Household Head DOB": ("headdobdistrict.csv", "headdoblocation.csv"),
                    "Household Head Education": ("headedudistrict.csv", "headedulocation.csv"),
                    "Household Head ID": ("headiddistrict.csv", "headidlocation.csv"),
                    "Household Member Names": ("namesdistrict.csv", "membernameslocation.csv"),
                    "Orphans": ("opharndistrict.csv", "opharnlocation.csv"),
                    "Relationship to Head": ("relatioshipheaddistrict.csv", "relatioshipheadlocation.csv"),
                    "Household Size": ("sizedistrict.csv", "sizelocation.csv"),
                    "Spouse DOB": ("spousedobdistrict.csv", "spousedoblocation.csv"),
                    "Spouse Education": ("spouseedudistrict.csv", "spouseedulocation.csv"),
                    "Spouse ID": ("spouseiddistrict.csv", "spouseidlocation.csv"),
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

                st.write(f"#### {selected_dataset} Dataset Visualizations")

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

elif county_option == "Narok":
    # landing_page()  # Show landing page

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
        # st.title("Data Visualization")
        st.write("### Select a variable")

        # Define datasets
        datasets = [
            "Declined Consent", "Floor", "Roof", "Lighting",
            "Habitable Rooms", "Cooking Fuel", "Waste Disposal",
            "Water Source", "Wall",
            "Household Head DOB", "Household Head Education", "Household Head ID", "Household Member Names", "Orphans",
            "Relationship to Head", "Household Size", "Spouse DOB", "Spouse Education", "Spouse ID", "Kisii County Summary"
        ]

        # Split datasets into two columns
        col1, col2 = st.columns(2)
        selected_datasets = []

        with col1:
            for dataset in datasets[:10]:
                if dataset != "Kisii County Summary":
                    if st.checkbox(dataset):
                        selected_datasets.append(dataset)

        with col2:
            for dataset in datasets[10:]:
                if st.checkbox(dataset):
                    selected_datasets.append(dataset)

        # Display the selected dataset
        if "Kisii County Summary" in selected_datasets:
            st.write("###Total Variable Mismmatch in Kisii County")

            summary_data = {
                "HH Variable": [
                    "HH Head ID Number", "HH Head Date of Birth", "Spouse ID Number", "Spouse Date of Birth",
                    "Household Size", "Household member names", "Education Levels of HH Head", "Education levels of Spouse",
                    "Orphan members", "Relationships to household head", "Number of main rooms", "Floor", "Wall", "Roof",
                    "Source of Water", "Source of Lighting", "Toilet type", "Cooking fuel", "Any Disabled"
                ],
                "Percentage": [3.6, 7.5, 10.6, 6.3, 9.9, 0.0, 54.1, 53.6, 57.6, 55.8, 57.1, 15.5, 22.3, 12.2, 57.7, 47.7, 48.1, 5.8,0.0]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_plot = plot_summary(summary_df,)

        elif len(selected_datasets) == 1:
            selected_dataset = selected_datasets[0]

            if selected_dataset == "Declined Consent":
                st.write("### Declined Consent Dataset Visualizations")

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
                    "Kisii County Summary": ("kisii_summary.csv",),
                    "Floor": ("floordistrict.csv", "floorlocation.csv", "floorvalues.csv", "Floor.x"),
                    "Roof": ("roofdistrict.csv", "rooflocation.csv", "roofvalues.csv", "Roof.x"),
                    "Lighting": ("lightingdistrict.csv", "lightinglocation.csv", "lightingvalues.csv", "LightingFuel.x"),
                    "Habitable Rooms": ("roomsdistrict.csv", "roomslocation.csv"),
                    "Cooking Fuel": ("cookingdistrict.csv", "cookinglocation.csv", "cookingvalues.csv", "CookingFuel.x"),
                    "Waste Disposal": ("toilet district.csv", "toiletlocation.csv", "toiletvalues.csv", "HumanWasteDisposal.x"),
                    "Water Source": ("waterdistrict.csv", "waterlocation.csv", "watervalues.csv", "WaterSource.x"),
                    "Wall": ("walldistrict.csv", "wall location.csv", "wallvalues.csv", "Wall.x"),
                    "Household Head DOB": ("headdobdistrict.csv", "headdoblocation.csv"),
                    "Household Head Education": ("headedudistrict.csv", "headedulocation.csv"),
                    "Household Head ID": ("headiddistrict.csv", "headidlocation.csv"),
                    "Household Member Names": ("namesdistrict.csv", "membernameslocation.csv"),
                    "Orphans": ("opharndistrict.csv", "opharnlocation.csv"),
                    "Relationship to Head": ("relatioshipheaddistrict.csv", "relatioshipheadlocation.csv"),
                    "Household Size": ("sizedistrict.csv", "sizelocation.csv"),
                    "Spouse DOB": ("spousedobdistrict.csv", "spousedoblocation.csv"),
                    "Spouse Education": ("spouseedudistrict.csv", "spouseedulocation.csv"),
                    "Spouse ID": ("spouseiddistrict.csv", "spouseidlocation.csv"),
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

                st.write(f"#### {selected_dataset} Dataset Visualizations")

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



elif county_option == "Samburu":
    # landing_page()  # Show landing page

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
        # st.title("Data Visualization")
        st.write("### Select a variable")

        # Define datasets
        datasets = [
            "Declined Consent", "Floor", "Roof", "Lighting",
            "Habitable Rooms", "Cooking Fuel", "Waste Disposal",
            "Water Source", "Wall",
            "Household Head DOB", "Household Head Education", "Household Head ID", "Household Member Names", "Orphans",
            "Relationship to Head", "Household Size", "Spouse DOB", "Spouse Education", "Spouse ID", "Kisii County Summary"
        ]

        # Split datasets into two columns
        col1, col2 = st.columns(2)
        selected_datasets = []

        with col1:
            for dataset in datasets[:10]:
                if dataset != "Kisii County Summary":
                    if st.checkbox(dataset):
                        selected_datasets.append(dataset)

        with col2:
            for dataset in datasets[10:]:
                if st.checkbox(dataset):
                    selected_datasets.append(dataset)

        # Display the selected dataset
        if "Kisii County Summary" in selected_datasets:
            st.write("###Total Variable Mismmatch in Kisii County")

            summary_data = {
                "HH Variable": [
                    "HH Head ID Number", "HH Head Date of Birth", "Spouse ID Number", "Spouse Date of Birth",
                    "Household Size", "Household member names", "Education Levels of HH Head", "Education levels of Spouse",
                    "Orphan members", "Relationships to household head", "Number of main rooms", "Floor", "Wall", "Roof",
                    "Source of Water", "Source of Lighting", "Toilet type", "Cooking fuel", "Any Disabled"
                ],
                "Percentage": [3.6, 7.5, 10.6, 6.3, 9.9, 0.0, 54.1, 53.6, 57.6, 55.8, 57.1, 15.5, 22.3, 12.2, 57.7, 47.7, 48.1, 5.8,0.0]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_plot = plot_summary(summary_df,)

        elif len(selected_datasets) == 1:
            selected_dataset = selected_datasets[0]

            if selected_dataset == "Declined Consent":
                st.write("### Declined Consent Dataset Visualizations")

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
                    "Kisii County Summary": ("kisii_summary.csv",),
                    "Floor": ("floordistrict.csv", "floorlocation.csv", "floorvalues.csv", "Floor.x"),
                    "Roof": ("roofdistrict.csv", "rooflocation.csv", "roofvalues.csv", "Roof.x"),
                    "Lighting": ("lightingdistrict.csv", "lightinglocation.csv", "lightingvalues.csv", "LightingFuel.x"),
                    "Habitable Rooms": ("roomsdistrict.csv", "roomslocation.csv"),
                    "Cooking Fuel": ("cookingdistrict.csv", "cookinglocation.csv", "cookingvalues.csv", "CookingFuel.x"),
                    "Waste Disposal": ("toilet district.csv", "toiletlocation.csv", "toiletvalues.csv", "HumanWasteDisposal.x"),
                    "Water Source": ("waterdistrict.csv", "waterlocation.csv", "watervalues.csv", "WaterSource.x"),
                    "Wall": ("walldistrict.csv", "wall location.csv", "wallvalues.csv", "Wall.x"),
                    "Household Head DOB": ("headdobdistrict.csv", "headdoblocation.csv"),
                    "Household Head Education": ("headedudistrict.csv", "headedulocation.csv"),
                    "Household Head ID": ("headiddistrict.csv", "headidlocation.csv"),
                    "Household Member Names": ("namesdistrict.csv", "membernameslocation.csv"),
                    "Orphans": ("opharndistrict.csv", "opharnlocation.csv"),
                    "Relationship to Head": ("relatioshipheaddistrict.csv", "relatioshipheadlocation.csv"),
                    "Household Size": ("sizedistrict.csv", "sizelocation.csv"),
                    "Spouse DOB": ("spousedobdistrict.csv", "spousedoblocation.csv"),
                    "Spouse Education": ("spouseedudistrict.csv", "spouseedulocation.csv"),
                    "Spouse ID": ("spouseiddistrict.csv", "spouseidlocation.csv"),
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

                st.write(f"#### {selected_dataset} Dataset Visualizations")

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



else:
    st.write("No data for the selected County")
