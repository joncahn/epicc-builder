import streamlit as st
import panda as pd

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
