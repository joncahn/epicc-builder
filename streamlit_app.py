import streamlit as st
import pandas as pd
import re
import yaml
import requests
from pathlib import Path

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
            st.error(f'❌ Duplicated rows: {name(r)} 😕')
            err=1
    for i, (_,row) in enumerate(tab.iterrows(), start=1):
        if not validate_sample_type(row):
            st.error(f'❌ Row #{i} {name(row)}: sample_type in does not match the data type 😕')
            err=1
        if not validate_SRA(row):
            st.error(f'❌ Row #{i} {name(row)}: fastq_path should be set to "SRA" to dowload deposited SRR run or to local directory otherwise 😕')
            err=1
        if assign_chip_input(row, tab) == "Input":
            st.error(f'❌ Row #{i} {name(row)}: missing a corresponding Input sample 😕')
            err=1
        elif assign_chip_input(row, tab) == "Sample":
            st.error(f'❌ Row #{i} {name(row)}: no sample depends on this Input 😕')
            err=1

    if err == 0:
        st.success("✅ Samplefile is correct! 🥳")

st.header("Click the button to check your sample file!", divider="red")

left, middle, right = st.columns(3)
with middle:
    epibtn = st.button("EPIGENETIC 🔘", type="primary", key=epibtn)
    
if epibtn: 
    check_table(edited)
        
##
st.header("Config file", divider="red")
url2 = "https://raw.githubusercontent.com/joncahn/epigeneticbutton/refs/heads/main/config/config.yaml"
response = requests.get(url2)
if response.status_code == 200:
        config = yaml.safe_load(response.text)
else:
        left, middle, right = st.columns(3)
        with middle:
        st.error("⛔ Failed to load YAML from GitHub ⛔")
        st.write("Sorry, you're on your own! Please refer to the EPICC github")
        st.link_button("back to EPICC github", "https://github.com/joncahn/epigeneticbutton")

st.subheader("Required parameters")
config['repo_folder'] = st.text_input("full path to folder:", value="/path/to/epigeneticbutton/repo", help="full path to where the epigeneticbutton github is cloned")
config['analysis_name'] = st.text_input("name of the run:", value="test_smk", help="label for analysis plots")
config['sample_file'] = st.text_input("path to sample file:", value="config/all_samples.tsv", help="path to the sample file created above")
config['ref_path'] = st.text_input("path to reference genome directory:", value="path/to/reference/genomes", help="path the the directory which contains all the subdirectories named like 'reference_genome' column above that contains the fasta and annotation files")
config['species'] = st.text_input("Species name:", value="thaliana", help="'thaliana' and 'mays' are already prepared. A new value will require additional input")

if config['species'] not in ["thaliana","mays"]:
        config[config['species']]['star_index'] = st.number_input("number for STAR genomeSAindexNbases", min_value=12, max_value=16, value=12)
        config[config['species']]['genomesize'] = st.number_input("genome size:", value=1.3e8, format="%.2e")
        config[config['species']]['ncbiID'] = st.text_input("NCBI species ID", value="3702") 
        config[config['species']]['genus'] = st.text_input("genus", value="Arabidopsis")
        config[config['species']]['go_database'] = st.text_input("GO database", value="org.Athaliana.eg.db", help="pattern should be org.<firstlettergenus><species>.eg.db")

st.subheader("Output options")
config['QC_option'] = st.selectbox("Choose fastQC options", ["none", "all"])
config['full_analysis'] = st.toggle("Complete analysis", value=True)
if config['full_analysis']:
        st.write("Complete analysis activated! Smash that button! 💪")
else:
        st.write("Complete analysis deactivated. Only mapping will be performed. 😞")

config['GO'] = st.toggle("Gene Ontology analysis", value=False, help="Option to perform gene ontology analysis. Requires other input, see Help GO for more details.")
if config['GO']:
        st.write("Gene Ontology will be performed! Good luck! 🤞")
        ref_genome = st.text_input("Reference genome to perform GO", value="ColCEN", help="Other prepared option: B73_v5. Add the same name that the reference_genome column of your samplefils. See Help GO for more details.")
        config['gaf_file'][ref_genome] = st.text_input("GAF file", value="data/ColCEN_infoGO.tab.gz", help="File of association of Gene IDs with GO terms. See Help GO for more details.")
        config['gene_info_file'][ref_genome] = st.text_input("Gene info file", value="data/ColCEN_genes_info.tab.gz", help="File with details on Gene IDs. See Help GO for more details.")
else:
        st.write("Gene ontology deactivated. Probably safer! 😥")
config['motifs'] = st.toggle("Motifs analysis for TFs", value=True, help="Option to perform motifs analysis for transcription factors.")
if config['motifs']:
        st.write("Motifs analysis selected! 😀")
        config['jaspar_db'] = st.text_input("Database of existing motifs", value="data/JASPAR2024_CORE_plants_non-redundant_pfms_meme.txt", help="Database of existing motifs (can be found on Jaspar website) for tomtom analysis.") 
        config['allreps'] = st.toggle("Motifs on all replicates", value=False, help="Option to perform motifs on all replicates, not only on the merged files")
        if config['allreps']:
                st.write("Let's go! Motifs on all individual replicates it is! 💸")
else:
        st.write("No motifs analysis will be performed! 😢")

with st.expander("⚙️ Advanced Options", expanded=False):
        with st.expander("ChIP-seq samples", expanded=False):
                config['trimming_quality']['ChIP'] = st.text_input("parameters for trimming", key="chip_trimming", value="-q 10 -m 20")
                config['adapter1']['ChIP'] = st.text_input("adapter sequence", key="chip_adapter", value="AGATCGGAAGAGCACACGTCTGAAC")
                config['chip_mapping_option'] = st.selectbox("Choose ChIP mapping options", ["default", "repeat", "all", "repeatall"])
                config['chip_tracks']['binsize'] = st.number_input("binsize for bigwigs", min_value=1, max_value=int(1e6), value=1)
                config['chip_tracks']['params'] = st.text_input("parameters for generating bigwigs", value="--scaleFactorsMethod 'None' --normalizeUsing CPM --extendReads 300")
                config['chip_callpeaks']['params'] = st.text_input("parameters for peak calling with macs2", value = "--keep-dup 'all' --nomodel")
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
                config['trimming_quality']['RNA'] = st.text_input("parameters for trimming", key="rna_trimming", value="-q 10 -m 20")
                config['adapter1']['RNA'] = st.text_input("adapter sequence", key="rna_adapter1", value="AGATCGGAAGAGCACACGTCTGAAC")
                config['rna_tracks']['RNAseq']['strandedness'] = st.selectbox("RNA strandedness", ["reverse", "forward"], help="Default for RNA-seq libraries is reverse. Change if the library prep kit use different chemistry.")
                config['rna_tracks']['RNAseq']['multimap'] = st.selectbox("Mapped reads used for bigwigs", ["multiple","unique"], help="Choose whether unique or multimapped reads to be used for bigwig files") 
        
        with st.expander("mC samples", expanded=False):
                config['trimming_quality']['mC'] = st.text_input("parameters for trimming", key="mC_trimming", value="-q 10 -m 20")
                config['adapter1']['mC'] = st.text_input("adapter sequence", key="mC_adapter1", value="AGATCGGAAGAGCACACGTCTGAAC")
                config['mC_method'] = st.selectbox("mC library prep method", ["default","WGBS", "Pico", "EMseq"], help="Library preparation method for mC samples. Default is whole-genome bisulphite sequencing.")
                map_pe = st.number_input("Max insert length", min_value=100, max_value=int(50000), value=1000, help="Value used for --maxins parameter of bismark to limit the maximum distance between reads R1 and R2 in PE data.")
                config['mC_mapping'][config['mC_method']] = f"--maxins {map_pe}"
        with st.expander("sRNA samples", expanded=False):
                config['trimming_quality']['sRNA'] = st.text_input("parameters for trimming", key="srna_trimming", value="-q 10 -m 15")
                config['adapter1']['sRNA'] = st.text_input("adapter sequence", key="srna_adapter1", value="TGGAATTCTCGGGTGCCAAGG")
                config['structural_rna_depletion'] = st.toggle("Depletion of structural RNAs", value=False, help="Option to filter structural RNA (rRNAs, tRNAs, snoRNAs) before mapping. Recommended step when studying microRNAs and small interfering RNAs. Requires other input, see Help Rfam.")
                if config['structural_rna_depletion']:
                        st.write("Depletion of structural RNA will be performed! Good riddance! 🧹")
                        config['structural_rna_file'] = st.text_input("Fasta file of structural RNAs to use for depletion", value="data/zm_structural_RNAs.fa.gz", help="Default to structural RNAs from Zea mays, prepared through Rfam. See Help Rfam for more details.")
                else:
                        st.write("No structural RNA depletion. rRNAs, here we come! 🪡")
                config['srna_mapping_params'] = st.text_input("Mapping parameters for sRNA  with ShortStack", value="--mmap u --dicermin 21 --dicermax 24 --dn_mirna --no_bigwigs", help="consider replacing --dn_mirna with --known_miRNAs KNOWN_MIRNAS.fa (but requires fetching miRNAs sequences, from miRBase for example)")
                config['srna_min_size'], config['srna_max_size'] = st.slider("Range of small RNA sizes to keep and create individual bigwig files", min_value=15, max_value=100, value=(21,24), help="A bigiwig file will be created for each integer value in this range, so don't go too crazy!")
                srna_heatmap_size = []
                st.write("Select the sizes to use for plotting in heatmaps and profiles:")
                for i in range(srna_min_size, srna_max_size + 1):
                        default_on = i in [21,24]
                        if st.checkbox(f"Plot {i}nt sRNAs", key=f"chk_{i}", value=default_on):
                                srna_heatmap_size.append(i)
                config['srna_heatmap_sizes'] = srna_heatmap_size
        with st.expander("Plotting options", expanded=False):
                config['heatmap_scales'] = st.selectbox("Scales for heatmaps", options=["type","sample","default"], help="'default' = default scaling from deeptools, same scale for all samples; 'sample' = each individual sample has its own scale; 'type' = each type of data is on a different scale (each ChIP mark + each TF + RNA + sRNA + each mC context)")
                config['stranded_heatmaps'] = st.toggle("Stranded heatmaps", value=True, help="Chose whether the heatmap should be done with stranded information or not. If true, lines in the bedfile without strand information (6th column '+' or '-') will not be included.")
                if config['stranded_heatmaps']:
                        st.write("If possible, heatmaps will be split by strand and then merged! Awesome! 🔀")
                else:
                        st.write("No strandedness in my heatmaps, thank you ➡️")
                config['heatmaps_sort_options'] = st.selectbox("Sort option for heatmaps", options=["mean","median","no"], help="mean = '--sortRegions descend --sortUsing mean'; 'median' = '--sortRegions descend --sortUsing median'; no = '--sortRegions keep'")
                config['profiles_scale'] = st.selectbox("Values for metaplots", options=["mean","median"])
                config['profiles_plot_params'] = st.text_input("Parameters for deeptools plotProfile", value="--plotType 'lines'")
                
st.write("More options are available to those who can directly change the yamls..." 🤓)
##
st.header("Click the buttons to create your files!", divider="red")

tab = edited.to_csv(sep="\t", index=False, encoding="utf-8")
yaml_str = yaml.dump(config, sort_keys=False)
buffer = io.BytesIO()
buffer.write(yaml_str.encode("utf-8"))
buffer.seek(0)

left, right = st.columns(2)
with left:
        st.download_button("Config 🔘",
                           data=buffer,
                           file_name="config.yaml",
                           mime="application/x-yaml",
                           type="primary",
                           key="configbtn")

with right:
        filename = Path(config["sample_file"]).name
        st.download_button("Samples 🔘",
                           data=tab,
                           file_name=filename,
                           mime="text/tab-separated-values",
                           type="primary",
                           key="configbtn")

        
