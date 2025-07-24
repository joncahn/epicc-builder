import streamlit as st
import pandas as pd
import re
import yaml
import requests

st.title(":red[EPICC-builder]")
st.text("Use this app to create your sample file and config file for the EPICC pipeline:\n"
        "For more details, see README at:")

left, middle, right = st.columns(3)
with middle:
        st.link_button("EPICC / epigeneticbutton", "https://github.com/joncahn/epigeneticbutton")

st.header("Sample file", divider="red")
url1 = "https://raw.githubusercontent.com/joncahn/epigeneticbutton/refs/heads/main/config/all_samples.tsv"
df = pd.read_csv(url1, sep="\t", header=None,
                      names=["data_type", "line", "tissue", "sample_type", "replicate", 
                             "seq_id", "fastq_path", "paired", "reference_genome"])

edited = st.data_editor(df, hide_index=True, num_rows="dynamic", column_config={
        "data_type": st.column_config.TextColumn(help="Type of data [RNAseq | ChIP_* | TF_* | mC | sRNA]", required=True, validate=r"^(RNAseq|ChIP.*|TF_.*|mC|sRNA)$"),
        "line": st.column_config.TextColumn(help="Can be any information you want to annotate and label samples", required=True, validate=r"^(?!.*\s)(?!.* )(?!.*__)(?!.*').*$"),
        "tissue": st.column_config.TextColumn(help="Can be any information you want to annotate and label samples", required=True, validate=r"^(?!.*\s)(?!.* )(?!.*__)(?!.*').*$"),
        "sample_type": st.column_config.TextColumn(help="Details on the type of sample: for RNAseq, mC and sRNA use RNAseq, mC and sRNA (or an equivalent), respectively. For TF ChIP, use IP (for narrow binding TF), IPb for broad binding, Input for the control. For histone ChIP-seq, use the name of the mark or Input", 
                                                   required=True, validate=r"^(?!.*\s)(?!.* )(?!.*__)(?!.*').*$"),
        "replicate": st.column_config.TextColumn(help="Name of replicate (e.g. 1, A, Rep1)", required=True, validate=r"^(?!.*\s)(?!.* )(?!.*__)(?!.*').*$"),
        "seq_id": st.column_config.TextColumn(help="SRR number, or unique identifier in the name of raw fastq files located at the fastq_path location", required=True, validate=r"^(?!.*\s)(?!.* )(?!.*__)(?!.*').*$"),
        "fastq_path": st.column_config.TextColumn(help="'SRA' if data to be download from SRA database or path to the directory containing the raw fastq files", required=True, validate=r"^(?!.*\s)(?!.* )(?!.*__)(?!.*').*$"),
        "paired": st.column_config.SelectboxColumn(help="Whether data is single-end (SE) or paired-end (PE)", required=True, options=["SE","PE"]),
        "reference_genome": st.column_config.TextColumn(help="Name of the reference genome to align the data to", required=True, validate=r"^(?!.*\s)(?!.* )(?!.*__)(?!.*').*$")
               })

# definitions:
def validations_patterns(data_type):
    if data_type == "RNAseq":
        return re.compile(r"^RNAseq$")
    elif data_type == "RAMPAGE":
        return re.compile(r"^RAMPAGE$")
    elif data_type == "sRNA":
        return re.compile(r"^(sRNA|smallRNA|shRNA)$")
    elif data_type == "mC":
        return re.compile(r"^(mC|WGBS|ONT|Pico|EMseq)$")
    elif data_type.startswith("TF_"):
        return re.compile(r"^(IP|IPb|Input)$")
    elif data_type.startswith("ChIP"):
        return re.compile(r"^(?!.*\s)(?!.*__)(?!.*').*$")

def validate_sample_type(row):
    pattern = validations_patterns(row.data_type)
    return bool(pattern and pattern.fullmatch(row.sample_type))

def validate_SRA(row):
    id = str(row.seq_id)
    path = str(row.fastq_path)
    if id.startswith("SRR"):
        return path == "SRA"
    if path == "SRA":
        return id.startswith("SRR")
    return True

def name(row):
    return f"{row.data_type}_{row.line}_{row.tissue}_{row.sample_type}"

def assign_chip_input(row, tab):
    dtype = row.data_type
    stype = row.sample_type
    if (dtype.startswith("TF") or dtype.startswith("ChIP")): 
        if stype != "Input":
            match = tab[
                (tab["data_type"]==row.data_type) &
                (tab["line"]==row.line) &
                (tab["tissue"]==row.tissue) &
                (tab["sample_type"]=="Input") &
                (tab["reference_genome"]==row.reference_genome)]
            if match.empty:
                return "Input"

        if stype == "Input":
            match = tab[
                (tab["data_type"]==row.data_type) &
                (tab["line"]==row.line) &
                (tab["tissue"]==row.tissue) &
                (tab["sample_type"] != "Input") &
                (tab["reference_genome"]==row.reference_genome)]
            if match.empty:
                return "Sample"          
    return True

def check_table(tab):
    err=0
    dup = tab[tab.duplicated(subset=["data_type","line","tissue","sample_type","replicate","reference_genome"], keep=False)]
    if not dup.empty:
        for _,r in dup.iterrows():
            st.error(f'❌ Duplicated rows: {name(r)}')
            err=1
    for i, (_,row) in enumerate(tab.iterrows(), start=1):
        if not validate_sample_type(row):
            st.error(f'❌ Row #{i} {name(row)}: sample_type in does not match the data type')
            err=1
        if not validate_SRA(row):
            st.error(f'❌ Row #{i} {name(row)}: fastq_path should be set to "SRA" to dowload deposited SRR run or to local directory otherwise')
            err=1
        if assign_chip_input(row, tab) == "Input":
            st.error(f'❌ Row #{i} {name(row)}: missing a corresponding Input sample')
            err=1
        elif assign_chip_input(row, tab) == "Sample":
            st.error(f'❌ Row #{i} {name(row)}: no sample depends on this Input')
            err=1

    if err == 0:
        st.success("✅ Samplefile is correct!")

##
st.header("Config file", divider="red")
url2 = "https://raw.githubusercontent.com/joncahn/epigeneticbutton/refs/heads/main/config/config.yaml"
response = requests.get(url2)
if response.status_code == 200:
        config = yaml.safe_load(response.text)
else:
        st.error("Failed to load YAML from GitHub")

st.subheader("Required parameters")
repo_folder = st.text_input("full path to folder:", value="/path/to/epigeneticbutton/repo", help="full path to where the epigeneticbutton github is cloned")
analysis_name = st.text_input("name of the run:", value="test_smk", help="label for analysis plots")
sample_file = st.text_input("path to sample file:", value="config/all_samples.tsv", help="path to the sample file created above")
ref_path = st.text_input("path to reference genome directory:", value="path/to/reference/genomes", help="path the the directory which contains all the subdirectories named like 'reference_genome' column above that contains the fasta and annotation files")
species = st.text_input("Species name:", value="thaliana", help="thaliana and mays are already prepared. A new value will require additional input")

if species not in ["thaliana","mays"]:
        star_index = st.number_input("number for STAR genomeSAindexNbases", min_value=12, max_value=16, value=12)
        genomesize = st.number_input("genome size:", value=int(1.3e8))
        ncbiID = st.text_input("NCBI species ID", value="3702") 
        genus = st.text_input("genus", value="Arabidopsis")
        go_database = st.text_input("GO database", value="org.Athaliana.eg.db", help="pattern should be org.<firstlettergenus><species>.eg.db")

st.subheader("Output options")
full_analysis = st.toggle("Complete analysis", value=True)
if full_analysis:
        st.write("Complete analysis activated!")
else:
        st.write("Complete analysis deactivated. Only mapping will be performed.")
QC_option = st.selectbox("Choose fastQC options", ["none", "all"])
chip_mapping_option = st.selectbox("Choose ChIP mapping options", ["default", "repeat", "all", "repeatall"])

with st.expander("⚙️ Advanced Options", expanded=False):
        with st.expander("ChIP-seq samples", expanded=False):
                trimming_quality = st.text_input("parameters for trimming", value="-q 10 -m 20")
                adapter1 = st.text_input("adapter sequence", value="AGATCGGAAGAGCACACGTCTGAAC")
                bs = st.number_input("binsize for bigwigs", min_value=1, max_value=int(1e6), value=1)
                params_bw = st.text_input("parameters for generating bigwigs", value="--scaleFactorsMethod 'None' --normalizeUsing CPM --extendReads 300")
                params_macs2 = st.text_input("parameters for peak calling with macs2", value = "--keep-dup 'all' --nomodel")
                peaktype = config["chip_callpeaks"]["peaktype"]
                st.markdown("Current peaktypes per mark:")
                for pattern, peak_type in peaktype.items():
                        st.markdown(f"{pattern}: `{peak_type}`")
                new_pattern = st.text_input("New or update histone mark", key="new_pattern").strip()
                new_type = st.radio("Peak type", ["narrow", "broad"], key="new_type")
                if st.button("Add or replace entry"):
                        if new_patttern:
                                peaktype = {k: v for k, v in peaktype.items() if k != new_pattern}
                                peaktype[new_pattern] = new_type
                                st.success(f"Pattern {new_pattern} set to {new_type}")
                        else:
                                st.error("Pattern is empty")
                config["chip_callpeaks"]["peaktype"] = peaktype
        with st.expander("RNAseq samples", expanded=False):
                strandedness = st.selectbox("RNA strandedness", ["reverse", "forward"], help="Default for RNA-seq libraries is reverse. Change if the library prep kit use different chemistry.")
                multimap = st.selectbox("Mapped reads used for bigwigs", ["multiple","unique"], help="Choose whether unique or multimapped reads to be used for bigwig files") 
        
        with st.expander("mC samples", expanded=False):
                mC_method = st.selectbox("mC library prep method", ["default","WGBS", "Pico", "EMseq"], help="Library preparation method for mC samples. Default is whole-genome bisulphite sequencing.")
                map_pe = st.number_input("Max inserts", min_value=100, max_value=int(50000), value=1000, help="Value used for --maxins parameter of bismark to limit the maximum distance between reads R1 and R2 in PE data.")
        
        with st.expander("mC samples", expanded=False):
                structural_rna_depletion = st.toggle("Depletion of structural RNAs", value=False, help="Option to filter structural RNA (rRNAs, tRNAs, snoRNAs) before mapping. Recommended step when studying microRNAs and small interfering RNAs.")
                if structural_rna_depletion:
                        st.write("Depletion of structural RNA will be performed!")
                        structural_rna_file = st.text_input("Fasta file of structural RNAs to use for depletion", value="data/zm_structural_RNAs.fa.gz", help="Default to structural RNAs from Zea mays, prepared through Rfam (see corresponding Help for more details)")
                else:
                        st.write("Complete analysis deactivated. Only mapping will be performed.")
                srna_mapping_params = st.text_input("Mapping parameters for sRNA  with ShortStack", value="--mmap u --dicermin 21 --dicermax 24 --dn_mirna --no_bigwigs", help="consider replacing --dn_mirna with --known_miRNAs KNOWN_MIRNAS.fa (but requires fetching miRNAs sequences, from miRBase for example)")
                srna_min_size, srna_max_size = st.slider("Range of small RNA sizes to keep and create individual bigwig files", min_value=20, max_value=100, value=(21,24))
                srna_heatmap_size = []
                st.write("Select the sizes to use for plotting in heatmaps and profiles:")
                for i in range(srna_min_size, srna_max_size + 1):
                        if st.checkbox(f"Include {i}", key=f"chk_{i}", value=True):
                                srna_heatmap_size.append(i)

##
st.header("Click the button to check your files!", divider="red")

left, middle, right = st.columns(3)
with middle:
    epibtn = st.button("EPIGENETIC 🔘", type="primary")
    
if epibtn: 
    check_table(edited)
        
