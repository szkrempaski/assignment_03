"""
process_files.py — Part 3: many files, one after another, with a running total.

The same job as process_file.py, but the app now remembers what it has already
done: how many files have been processed, how many packages that came to, and a
one-line summary of each file — and it keeps remembering across uploads.

That is the hard part, and it is hard for a specific reason: every interaction
reruns this whole script from the top, so an ordinary variable like
`files_processed = 0` is reset to zero on every rerun. Anything that has to
survive a rerun lives in `st.session_state` instead, and is initialised only
once — the first time the script runs.

The other trap is the uploader itself. Once a file has been chosen it stays
chosen on every rerun, so an app that processes "whenever there is a file" would
count the same file again on every interaction. Processing happens on a button
click instead: `st.button` is True only on the one rerun the click caused.

Run it:  Run and Debug -> "Streamlit Run: Current File"   (see README Reference #1)
Test it: pytest tests/test_streamlit.py -k process_files
"""

import json

import streamlit as st

from packaging_parser import parse_packaging, calc_total_units

# --- The page ---------------------------------------------------------------------

st.title("Process Package Files")

# 1. Initialise once — only exists after the first run, so this block only fires
#    the very first time the script executes for this session.
if "files_processed" not in st.session_state:
    st.session_state.files_processed = 0
    st.session_state.packages_processed = 0
    st.session_state.history = []

uploaded_file = st.file_uploader("Upload package file:", key="package_file")
clicked = st.button("Process file", key="process")

# 2. Update on the click. Choosing a file sets uploaded_file, but that alone
#    changes nothing — only a click on this exact rerun does the work.
if clicked and uploaded_file:
    text = uploaded_file.getvalue().decode("utf-8")

    packages = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        packages.append(parse_packaging(line))

    output_name = "data/" + uploaded_file.name.replace(".txt", ".json")
    with open(output_name, "w") as json_file:
        json.dump(packages, json_file, indent=4)

    st.session_state.files_processed += 1
    st.session_state.packages_processed += len(packages)
    st.session_state.history.append(
        f"{len(packages)} packages written to {output_name}"
    )

# 3. Display from state — every run, regardless of whether a click just happened.
col1, col2 = st.columns(2)
col1.metric("Files processed", st.session_state.files_processed)
col2.metric("Packages processed", st.session_state.packages_processed)

for line in st.session_state.history:
    st.info(line)