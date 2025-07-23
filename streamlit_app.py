import streamlit as st
import panda as pd

df = pd.DataFrame(
    [
            {"data_type": "ChIP", "line": "B73", "tissue": "ears"}


)
- `data_type`: Type of data [RNAseq | ChIP_* | TF_* | mC | sRNA] (RAMPAGE under development)
   - `line`: Sample line (e.g., B73)
   - `tissue`: Tissue type
   - `sample_type`: Sample identifier
   - `replicate`: Replicate ID
   - `seq_id`: Sequencing ID; use the corresponding SRR####### if downloading from SRA
   - `fastq_path`: Path to FASTQ files; if downloading from SRA, use "SRA" 
   - `paired`: [PE | SE]
   - `ref_genome`: Reference genome name
