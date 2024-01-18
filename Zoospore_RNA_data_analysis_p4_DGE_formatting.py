"""
Zoospore RNA Manuscript: RNA Data Analysis for Specific Annotations

@author: Lazarina Butkovich
"""
import os
from os.path import join as pjoin
import pandas as pd

"""
This script is designed to analyze the DESeq2-processed RNA-seq data comparing N. californiae zoospore vs fungal mat samples, in order to perform differential gene expression analysis for specific gene annotations. This script should be run after the content in the first RNA data analysis script has been run. This script can be modified to consider various annotations (ie: secondary metabolites, transcription factors, specific genes highlighted in published papers) that are not already readily encapsulated in the broad annotation categories (ie: KOG, GO, KEGG, IPR), or need extra formatting.
"""

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
Functions
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def check_ID_column(pd_df, id_name="proteinID"):
    """
    The function check_ID_column checks if the ID column id_name is present in the pandas dataframe, pd_df.

    inputs:
    pd_df: pandas dataframe
    id_name: name of id column, default set to 'proteinID' (string)

    output:
    boolean: True if id_name column in pd_df, exit if not
    """
    if id_name in pd_df.columns:
        return
    else:
        print("Error: no expected " + id_name + " column in pd_df")
        exit()

def make_proteinID_annot_dict(pd_annot, annot_col, id_name="proteinID"):
    """
    The function make_proteinID_annot_dict makes a dictionary with proteinIDs as keys and annotations as values from the annot_col column of the pandas dataframe pd_annot. The function removes duplicate annotations for a given ID. Multiple annotations for a single ID are all kept and separated by a comma in a single value string. Each proteinID key will therefore only have 1 value string. The purpose of this formatting is to prepare the data for addition to the summary dataframe, with the single string as a value in a column.

    inputs:
    pd_annot: pandas dataframe with annotations
    - must have id_name (string) column
    annot_col: specific column name (string) with annotations
    id_name: name of id column, default set to 'proteinID' (string)

    output:
    proteinID_annot_dict: dictionary with IDs as keys and annotations listed (sep=', ') as the values. Remove duplicate annotations for a given ID.
    """
    proteinID_annot_dict = {}
    # if no proteinID (or id_name) column in pd_annot, print error message
    check_ID_column(pd_annot, id_name)
    for i in range(len(pd_annot)):
        proteinID = pd_annot[id_name][i]
        annot = pd_annot[annot_col][i]
        if proteinID in proteinID_annot_dict:
            # if annot is different from proteinID_annot_dict[proteinID] ...
            # (I don't want duplicates of same annotation values)
            if annot not in proteinID_annot_dict[proteinID]:
                # ... then append annot to proteinID_annot_dict[proteinID]
                proteinID_annot_dict[proteinID].append(annot)
        else:
            proteinID_annot_dict[proteinID] = [annot]
    for key in proteinID_annot_dict:
        if len(proteinID_annot_dict[key]) > 1:
            vals = list(map(str, proteinID_annot_dict[key]))
            proteinID_annot_dict[key] = ",".join(vals)
        else:
            proteinID_annot_dict[key] = proteinID_annot_dict[key][0]
    return proteinID_annot_dict

def add_to_df(df, X_annot_pd, annot_cols_list, shared_col='proteinID'):
    """
    The function add_to_df adds annotation columns from the pandas dataframe X_annot_pd to the pandas dataframe df. The function returns df with the new columns. For example, df is the DGE_summary dataframe and X_annot_pd could be the KOG annotations dataframe.

    inputs: 
    df: pandas dataframe with proteinIDs
    X_annot_pd: pandas dataframe with proteinIDs and annotations
    annot_cols_list: list of column names in X_annot_pd to add to DGE_summary (list of strings)
    shared_col: column name in df and X_annot_pd that is shared (string) default set to proteinID

    output: df with new columns (pandas dataframe)
    """
    X_dicts_list = []
    for col in annot_cols_list:
        X_dicts_list.append(make_proteinID_annot_dict(X_annot_pd, col, shared_col))

    # Add annotations to df
    annot_col_num = 0
    for annot_dict in X_dicts_list:
        df[annot_cols_list[annot_col_num]] = df[shared_col].map(annot_dict)
        annot_col_num += 1

    return df

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
Import Files and Make Annotation Dataframes
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# Import files
input_folder = r'input' 
output_folder = r'output'

# Create output folder if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# A) Essential file:
# DGE summary from 1st script 
DGE_summary_filename = "DGE_summary_output.xlsx"
DGE_summary = pd.read_excel(pjoin(*[output_folder, DGE_summary_filename]), sheet_name='DGE_summary')

# B) Specific annotation types (You can modify these, or add/remove files and subsequent corresponding code, as needed for your application)

# Secondary Metabolites
SM_annot_filename = "Neosp1_SMs_orthologs_20221024.xlsx"
SM_annot = pd.read_excel(pjoin(*[input_folder, SM_annot_filename]), sheet_name='SMs')

# Hydrogenosomes
hydrogenosome_annot_filename = "G1_hydrogenosomes.xlsx"
hydrogenosome_annot = pd.read_excel(pjoin(*[input_folder, hydrogenosome_annot_filename]), sheet_name='Hsome function')
hydrogenosome_localization_annot = pd.read_excel(pjoin(*[input_folder, hydrogenosome_annot_filename]), sheet_name='localization notes')

# SWEETs
SWEET_annot_filename = "G1_SWEETs.xlsx"
SWEET_annot = pd.read_excel(pjoin(*[input_folder, SWEET_annot_filename]), sheet_name='Sheet1')

# Transcription factors (TFs)
TF_annot_filename = 'G1_transcription_factors_20230316.xlsx'
TF_annot = pd.read_excel(pjoin(*[input_folder, TF_annot_filename]), sheet_name='Sheet1')

# Unfolded protein response genes and heat shock response genes from 2016 S. Seppala Microb Cell Fact paper
UPR_HSR_annot_filename = 'G1_UPR_HSR.csv'
UPR_HSR_annot = pd.read_csv(pjoin(*[input_folder, UPR_HSR_annot_filename]))

# I ran local BLASTp of G1 genes to a downloaded FASTA file of TCDB (Transporter Classification Database) proteins
# I used a script to process/filter the BLASTp results
tcdb_blast_filename = "output_TCDB_BLASTp_filtered.csv"
tcdb_blast = pjoin(*[input_folder, tcdb_blast_filename])
tcdb_blast = pd.read_csv(tcdb_blast)

# Import info on transporter family, ChEBID, and superfamily
tcdb_fam_desc_filename = "TC_specific_family_defs.csv"
tcdb_chebid_filename = "TC_ChEBI_IDs.csv"
tcdb_superfam_desc_filename = "TC_superfamily_defs.csv"
# Import TC def data into dataframes. These files already have headers
tcdb_fam_desc = pd.read_csv(pjoin(*[input_folder, tcdb_fam_desc_filename]))
tcdb_chebid = pd.read_csv(pjoin(*[input_folder, tcdb_chebid_filename]))
tcdb_superfam_desc = pd.read_csv(pjoin(*[input_folder, tcdb_superfam_desc_filename]))

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
Expand upon annotations in DGE_summary
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""
Formatting Secondary Metabolites Excel
"""
# if rows in SM_annot have identical values, remove duplicates
SM_annot = SM_annot.drop_duplicates()
# Drop nan in proteinID column for SM_annot
SM_annot = SM_annot.dropna(subset=['proteinID'])

# Make SM tabs
# Filter DGE_summary for rows with a value in the SM_cluster_id column
SMs = DGE_summary[DGE_summary['SM_cluster_id'].notna()]

# Make the last 3 columns appear at the beginning of the dataframe and remove some columns
SMs = SMs[['proteinID','SM_cluster_id','SM_cluster_type', 'SM_scaffold', 'SM_core', 'log2FC', 'padj', 'sig', 'mat_counts_avg', 'zoosp_counts_avg',	'mat_tpm_avg', 'zoosp_tpm_avg', 'mat_upreg', 'zoosp_upreg']]

# Sort SMs by proteinID
SMs = SMs.sort_values(by=['proteinID'])
# Sort SM_annot by proteinID
SM_annot = SM_annot.sort_values(by=['proteinID'])

# Reset index
SMs = SMs.reset_index(drop=True)
SM_annot = SM_annot.reset_index(drop=True)

# Add the remaining columns that I did not add in the first data analysis script, starting from column Scaffold
# list the last 20 columns of SM_annot
new_SM_cols = list(SM_annot.columns)[6:]
SMs = add_to_df(SMs, SM_annot, new_SM_cols)

# Format the SM columns
SMs['SM_core'] = [True if val == 1 else False for val in list(SMs['SM_core'])]
# Extract the cluster number from SM_cluster_id, which are the values after 'Neosp1.' Make this value an int
# Insert 'SM_cluster_id_num' column after 'SM_cluster_id' column
SMs.insert(1, 'SM_cluster_id_num', [val.split('Neosp1.')[1] for val in list(SMs['SM_cluster_id'])])
SMs['SM_cluster_id_num'] = [int(val) for val in list(SMs['SM_cluster_id_num'])]

# Order SMs by SM_cluster_id_num and then by Order_in_BGC if there are ties
SMs.sort_values('Order_in_BGC', ascending=True, na_position='last', inplace=True)
SMs.sort_values('SM_cluster_id_num', ascending=True, na_position='last', kind='mergesort', inplace=True)

# Core_SMs df (SMs with SM_core == True)
Core_SMs = SMs[SMs['SM_core'] == True]

"""
Formatting Hydrogenosomes excel
"""
# if rows in hydrogenosome_annot have identical values, remove duplicates
hydrogenosome_annot = hydrogenosome_annot.drop_duplicates()
# Drop nan in proteinID column for hydrogenosome_annot
hydrogenosome_annot = hydrogenosome_annot.dropna(subset=['proteinID'])
# Sort hydrogenosome_annot by proteinID
hydrogenosome_annot = hydrogenosome_annot.sort_values(by=['proteinID'])
# Remove G1 protein column
hydrogenosome_annot = hydrogenosome_annot.drop(columns=['G1 protein'])

# if rows in hydrogenosome_localization_annot have identical values, remove duplicates
hydrogenosome_localization_annot = hydrogenosome_localization_annot.drop_duplicates()
# Drop nan in proteinID column for hydrogenosome_localization_annot
hydrogenosome_localization_annot = hydrogenosome_localization_annot.dropna(subset=['proteinID'])
# Sort hydrogenosome_localization_annot by proteinID
hydrogenosome_localization_annot = hydrogenosome_localization_annot.sort_values(by=['proteinID'])

# Align hydrogenosome_annot and hydrogenosome_localization_annot by proteinID
hydrogenosome_annot = hydrogenosome_annot.reset_index(drop=True)
hydrogenosome_localization_annot = hydrogenosome_localization_annot.reset_index(drop=True)
# Add hydrogenosome_localization columns to hydrogenosome_annot (columns: ecNum, Mitochondria, Plastid (mito), Cytoplasm, Peroxisome, Soluble?)
hydrogenosome_annot = add_to_df(hydrogenosome_annot, hydrogenosome_localization_annot, ['ecNum', 'Mitochondria', 'Plastid (mito)', 'Cytoplasm', 'Peroxisome', 'Soluble?'])

# Remove rows in hydrogenosome_annot that do not have a row in DGE_summary. There should be 69 proteinIDs and proteinIDs with identical aa sequences should have been pre-consolidated in the hydrogenosome_annot file
hydrogenosome_annot = add_to_df(hydrogenosome_annot, DGE_summary, ['log2FC','padj','sig','mat_tpm_avg','zoosp_tpm_avg','mat_upreg','zoosp_upreg', 'proteinID_Ortho_format', 'Orthogroup',	'anasp1_ortholog',	'caecom1_ortholog',	'neosp1_ortholog', 'pirfi3_ortholog', 'S4 orthologs', 'S4 ortholog counts', 'CC orthologs', 'CC ortholog counts', 'G1 orthologs', 'G1 ortholog counts', 'PF orthologs', 'PF ortholog counts'])

"""
Formatting SWEET Transporters Excel
"""
# filter DGE_summary for SWEET transporters (proteinIDs matching values in list SWEET_annot)
SWEET_annot = add_to_df(SWEET_annot, DGE_summary, ['log2FC','padj','sig','mat_tpm_avg','zoosp_tpm_avg','mat_upreg','zoosp_upreg', 'proteinID_Ortho_format', 'Orthogroup',	'anasp1_ortholog',	'caecom1_ortholog',	'neosp1_ortholog', 'pirfi3_ortholog', 'S4 orthologs', 'S4 ortholog counts', 'CC orthologs', 'CC ortholog counts', 'G1 orthologs', 'G1 ortholog counts', 'PF orthologs', 'PF ortholog counts'])

"""
Formatting Transcription Factors Excel
"""
# filter DGE_summary for transcription factors (proteinIDs matching values in list TF_annot)
# See Materials and Methods section for how the transcription factors were identified
# Get all column names of DGE_summary
DGE_summary_cols = list(DGE_summary.columns)
# Remove 'proteinID' from DGE_summary_cols
DGE_summary_cols.remove('proteinID')
TF_annot = add_to_df(TF_annot, DGE_summary, DGE_summary_cols)

"""
UPR and HSR genes
"""
UPR_HSR_annot = add_to_df(UPR_HSR_annot, DGE_summary, ['log2FC','padj','sig','mat_tpm_avg','zoosp_tpm_avg','mat_upreg','zoosp_upreg', 'proteinID_Ortho_format', 'Orthogroup',	'anasp1_ortholog',	'caecom1_ortholog',	'neosp1_ortholog', 'pirfi3_ortholog', 'S4 orthologs', 'S4 ortholog counts', 'CC orthologs', 'CC ortholog counts', 'G1 orthologs', 'G1 ortholog counts', 'PF orthologs', 'PF ortholog counts'])

"""
Transporters from TCDB (Transporter Classification Database)
"""
# I ran local BLASTp of G1 genes to a downloaded FASTA file of TCDB proteins
# I used a script to process/filter the BLASTp results
# Here, I want to align that output to DGE_summary
# Additionally, I use the subject_seq_id column to extract additional info about each TCDB protein

# Change first column query_seq_id to proteinID
tcdb_blast.rename(columns={'query_seq_id':'proteinID'}, inplace=True)
# sort by ascending e_value
tcdb_blast.sort_values(by=['e_value'], inplace=True)
# reset index
tcdb_blast.reset_index(drop=True, inplace=True)
# tcdb_cols is list of all column names except for the first column, proteinID
tcdb_cols = list(tcdb_blast.columns)
tcdb_cols.remove('proteinID')
# add_to_df function will add columns from tcdb_blast to DGE_summary
tcdb_blast = add_to_df(DGE_summary, tcdb_blast, tcdb_cols)
# make a new dataframe tcdb_blast_filtered that is a copy of tcdb_blast and filter only for rows with a value in 'subject_seq_id'
tcdb_blast_filtered = tcdb_blast.copy()
tcdb_blast_filtered = tcdb_blast_filtered[tcdb_blast_filtered['subject_seq_id'].notnull()]
# Take the subject_seq_id data and extract the text after the last '|'. Put this text in a new column called 'TCID'
tcdb_blast_filtered['TCID'] = tcdb_blast_filtered['subject_seq_id'].str.split('|').str[-1]

# In tcdb_blast_filtered, make a new column that is the text before the 3rd '.' in TCID. If there is no 3rd '.', then make the value the whole text string in TCID
tcdb_blast_filtered['TCID_fam'] = tcdb_blast_filtered['TCID'].str.split('.').str[0:3].str.join('.')
# Make a column in tcdb_blast_filtered that matches the values from TCID_fam to TCID in tcdb_fam_desc. The value in this column will be the value in TC_family_desc
tcdb_blast_filtered = add_to_df(tcdb_blast_filtered, tcdb_fam_desc, ['TC_family_desc'],shared_col='TCID_fam')
# Make a column in tcdb_blast_filtered to describe superfamily. Use add_to_df with tcdb_blast_filtered and tcdb_superfam_desc, using TCID as shared_col
tcdb_blast_filtered = add_to_df(tcdb_blast_filtered, tcdb_superfam_desc, ['TC_superfamily_desc'],shared_col='TCID')
# Make a column in tcdb_blast_filtered to describe ChEBI ID. Use add_to_df with tcdb_blast_filtered and tcdb_chebid, using TCID as shared_col
tcdb_blast_filtered = add_to_df(tcdb_blast_filtered, tcdb_chebid, ['ChEBI_ID_desc'],shared_col='TCID')

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
Export files
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""
Write each dataframe to a different sheet in an output Excel
"""
name_out = "DGE_summary_output_formatted.xlsx"
file_path_out = pjoin(*[output_folder, name_out])

# https://xlsxwriter.readthedocs.io/example_pandas_multiple.html
writer = pd.ExcelWriter(file_path_out, engine='xlsxwriter')

# Write each dataframe to a different sheet (with no index column)
DGE_summary.to_excel(writer, sheet_name='DGE_summary',index=False)
SMs.to_excel(writer, sheet_name='all SMs',index=False)
Core_SMs.to_excel(writer, sheet_name='Core SMs',index=False)
hydrogenosome_annot.to_excel(writer, sheet_name='Hydrogenosomes',index=False)
SWEET_annot.to_excel(writer, sheet_name='SWEET transporters',index=False)
TF_annot.to_excel(writer, sheet_name='TFs',index=False)
UPR_HSR_annot.to_excel(writer, sheet_name='UPR and HSR',index=False)
tcdb_blast_filtered.to_excel(writer, sheet_name='TCDB Transporters',index=False)

"""
Excel conditional formatting
"""
workbook = writer.book
# In the excel 'all SMs' sheet, highlight mat_upreg values of 1
worksheet = writer.sheets['all SMs']
# Create a format to use in the conditional formatting. Make green highlight
format_green = workbook.add_format({'bg_color': '#C6EFCE',
                                    'font_color': '#006100'})
# create red highlight
format_red = workbook.add_format({'bg_color': '#FFC7CE',
                                 'font_color': '#9C0006'})
# create a bold format
format_bold = workbook.add_format({'bold': True})

# Apply a conditional format to the cell range.
worksheet.conditional_format('N2:N1000', {'type':     'cell',
                                            'criteria': '==',
                                            'value':    1,
                                            'format':   format_green})
# In the excel 'all SMs' sheet, highlight zoosp_upreg values of 1
worksheet.conditional_format('O2:O1000', {'type':     'cell', 'criteria': '==', 'value':    1, 'format':   format_green})

# In the excel 'core SMs' sheet, highlight mat_upreg values of 1
worksheet = writer.sheets['Core SMs']
worksheet.conditional_format('N2:N1000', {'type':     'cell', 'criteria': '==', 'value':    1, 'format':   format_green})
# In the excel 'core SMs' sheet, highlight zoosp_upreg values of 1
worksheet.conditional_format('O2:O1000', {'type':     'cell', 'criteria': '==', 'value':    1, 'format':   format_green})

# In Hydrogenosomes sheet, highlight mat_upreg values of 1
worksheet = writer.sheets['Hydrogenosomes']
# Ignore NaN values
worksheet.conditional_format('N2:N1000', {'type':     'cell', 'criteria': '==', 'value':    1, 'format':   format_green})
# In Hydrogenosomes sheet, highlight zoosp_upreg values of 1
worksheet.conditional_format('O2:O1000', {'type':     'cell', 'criteria': '==', 'value':    1, 'format':   format_green})

# Close the Pandas Excel writer and output the Excel file.
writer.close()