import streamlit as st
import pandas as pd
import re

st.title("Epicc-builder: create your sample file and config files for the epigenetic button")

st.header("Sample file")
df = pd.DataFrame(
    [
            {"data_type": "ChIP", "line": "B73", "tissue": "ears", "sample_type": "H3K27ac", "replicate": "Rep1", "seq_id": "k27ac.rep1", "fastq_path": "/local/path/fastqs", "paired": "PE", "reference_genome": "B73_v5"},
            {"data_type": "ChIP", "line": "B73", "tissue": "ears", "sample_type": "Input", "replicate": "Rep1", "seq_id": "input.rep1", "fastq_path": "/local/path/fastqs", "paired": "PE", "reference_genome": "B73_v5"},
            {"data_type": "ChIP_A", "line": "B73", "tissue": "ears", "sample_type": "H3K4me1", "replicate": "Rep1", "seq_id": "SRR49043094", "fastq_path": "SRA", "paired": "SE", "reference_genome": "B73_v5"},
            {"data_type": "ChIP_A", "line": "B73", "tissue": "ears", "sample_type": "Input", "replicate": "Rep1", "seq_id": "SRR49303293", "fastq_path": "SRA", "paired": "SE", "reference_genome": "B73_v5"},
            {"data_type": "TF_TB1", "line": "B73", "tissue": "leaves", "sample_type": "IP", "replicate": "Rep1", "seq_id": "SRR49303293", "fastq_path": "SRA", "paired": "SE", "reference_genome": "B73_v5"},
            {"data_type": "TF_TB1", "line": "B73", "tissue": "leaves", "sample_type": "Input", "replicate": "Rep1", "seq_id": "SRR49303293", "fastq_path": "SRA", "paired": "SE", "reference_genome": "B73_v5"},
            {"data_type": "RNAseq", "line": "B73", "tissue": "leaves", "sample_type": "RNAseq", "replicate": "Rep1", "seq_id": "SRR49303293", "fastq_path": "SRA", "paired": "SE", "reference_genome": "B73_v5"},
            {"data_type": "RNAseq", "line": "WT", "tissue": "leaves", "sample_type": "RNAseq", "replicate": "Rep2", "seq_id": "SRR49303293", "fastq_path": "SRA", "paired": "SE", "reference_genome": "B73_v5"},
            {"data_type": "RNAseq", "line": "WT", "tissue": "leaves", "sample_type": "RNAseq", "replicate": "Rep3", "seq_id": "SRR49303293", "fastq_path": "SRA", "paired": "SE", "reference_genome": "B73_v5"},
            {"data_type": "RNAseq", "line": "mutant", "tissue": "leaves", "sample_type": "RNAseq", "replicate": "Rep1", "seq_id": "SRR49303293", "fastq_path": "SRA", "paired": "SE", "reference_genome": "B73_v5"},
            {"data_type": "RNAseq", "line": "mutant", "tissue": "leaves", "sample_type": "RNAseq", "replicate": "Rep2", "seq_id": "SRR49303293", "fastq_path": "SRA", "paired": "SE", "reference_genome": "B73_v5"},
            {"data_type": "sRNA", "line": "W22", "tissue": "leaves", "sample_type": "sRNA", "replicate": "Rep1", "seq_id": "SRR49303293", "fastq_path": "SRA", "paired": "SE", "reference_genome": "W22_v2"},
            {"data_type": "sRNA", "line": "W22", "tissue": "leaves", "sample_type": "sRNA", "replicate": "Rep2", "seq_id": "SRR49303293", "fastq_path": "SRA", "paired": "SE", "reference_genome": "W22_v2"},
            {"data_type": "sRNA", "line": "W22", "tissue": "pollen", "sample_type": "sRNA", "replicate": "Rep1", "seq_id": "SRR49303293", "fastq_path": "SRA", "paired": "SE", "reference_genome": "W22_v2"},
            {"data_type": "sRNA", "line": "W22", "tissue": "pollen", "sample_type": "sRNA", "replicate": "Rep2", "seq_id": "SRR49303293", "fastq_path": "SRA", "paired": "SE", "reference_genome": "W22_v2"},
            {"data_type": "mC", "line": "Col0", "tissue": "WT", "sample_type": "mC", "replicate": "Rep1", "seq_id": "SRR49303293", "fastq_path": "SRA", "paired": "PE", "reference_genome": "W22_v2"},
            {"data_type": "mC", "line": "Col0", "tissue": "mutant", "sample_type": "mC", "replicate": "Rep1", "seq_id": "SRR49303293", "fastq_path": "SRA", "paired": "PE", "reference_genome": "W22_v2"}
        ]
)

allowed_dtypes=re.compile(r"^(RNAseq|ChIP_.*|TF_.*|mC|sRNA)$")
def validations_columns(data_type):
    if data_type == "RNAseq":
        return re.compile(r"^RNAseq$")
    elif data_type == "sRNA":
        return re.compile(r"^sRNA$")
    elif data_type == "mC":
        return re.compile(r"^mC$")
    elif data_type.startswith("TF_"):
        return re.compile(r"^(IP|IPb|Input)$")
    elif data_type.startswith("ChIP_"):
        return re.compile(r"^(?!.*[\s'"])(?!.*__).*$")
    
st.data_editor(df, hide_index=True, num_rows="dynamic", disabled=True, column_config={
        "data_type": st.column_config.SelectboxColumn(help="Type of data [RNAseq | ChIP_* | TF_* | mC | sRNA]", required=True, default="RNAseq", validate=allowed_dtypes),
        "line": st.column_config.TextColumn(help="Can be any information you want to annotate and label samples", required=True, default="WT", validate=r"^(?!.*[\s'"])(?!.*__).*$"),
        "tissue": st.column_config.TextColumn(help="Can be any information you want to annotate and label samples", required=True, default="RNAseq", validate=r"^(?!.*[\s'"])(?!.*__).*$"),
        "sample_type": st.column_config.TextColumn(help="Details on the type of sample: for RNAseq, mC and sRNA use RNAseq, mC and sRNA, respectively. For TF ChIP, use IP (for narrow binding TF), IPb for broad binding, Input for the control. For histone ChIP-seq, use the name of the mark or Input", 
                                                   required=True, default="Input", validate=validations_columns(data_type)),
        "replicate": st.column_config.TextColumn(help="Name of replicate (e.g. 1, A, Rep1)", required=True, default="Rep1", validate=r"^(?!.*[\s'"])(?!.*__).*$"),
        "seq_id": st.column_config.TextColumn(help="SRR number, or unique identifier in the name of raw fastq files located at the fastq_path location", required=True, validate=r"^(?!.*[\s'"])(?!.*__).*$"),
        "fastq_path": st.column_config.TextColumn(help="'SRA' if data to be download from SRA database or path to the directory containing the raw fastq files", required=True, default="SRA", validate=r"^(?!.*[\s'"])(?!.*__).*$"),
        "paired": st.column_config.SelectboxColumn(help="Whether data is single-end (SE) or paired-end (PE)", required=True, default="SE", options=["SE","PE"]),
        "reference_genome": st.column_config.TextColumn(help="Name of the reference genome to align the data to", required=True, validate=r"^(?!.*[\s'"])(?!.*__).*$")
               })

st.header("Config file")

st.header("Click the button to generate your files!")
st.button("EPIGENETIC")

