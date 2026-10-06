import json
import os
from datetime import datetime
import streamlit as st
from core import discover, brief, plan, demo

st.set_page_config(page_title='BioEvidence', page_icon='🧬', layout='wide')
st.title('🧬 BioEvidence')
st.write('From a biology question to a source-linked research starting point.')
st.caption('SerpApi-powered discovery · Public datasets · Transparent evidence review')

with st.sidebar:
    st.header('Search settings')
    key = st.text_input('SerpApi API key', value=os.getenv('SERPAPI_API_KEY', ''), type='password')
    year = st.number_input('Papers published from', min_value=1900, max_value=datetime.now().year, value=2020)
    resources = st.selectbox('Available computing', ['Laptop / browser only', 'Workstation / cloud computing'])
    st.caption('Each live search makes 3 SerpApi requests. Provider caching and account limits apply. Questions are sent to SerpApi.')
    sample = st.button('Explore synthetic demo')

with st.form('question'):
    question = st.text_area('Research question or keywords', value='Rice drought tolerance RNA-seq transcriptomics', max_chars=500)
    submitted = st.form_submit_button('Search papers and datasets')

if sample:
    st.session_state.bundle = demo(resources)
    st.session_state.version = st.session_state.get('version', 0) + 1
if submitted:
    if not key.strip():
        st.error('Enter a SerpApi key, or use the synthetic demo.')
    elif len(question.strip()) < 8:
        st.error('Enter a more specific question.')
    else:
        with st.spinner('Searching Scholar, GEO, and SRA…'):
            st.session_state.bundle = discover(key.strip(), question.strip(), year, resources)
        st.session_state.version = st.session_state.get('version', 0) + 1

bundle = st.session_state.get('bundle')
if bundle:
    st.subheader(bundle['question'])
    st.caption(f"{bundle['mode']} · {bundle['retrieved_at']}")
    if bundle['mode'].startswith('SYNTHETIC'):
        st.warning('Synthetic interface demonstration. These are not actual research results.')
    for error in bundle['errors']:
        st.warning(error)
    records = bundle['records']
    if not records:
        st.info('No usable results. Try fewer keywords or a wider year range.')
    else:
        a, b = st.columns(2)
        a.metric('Papers', sum(r['kind'] == 'Paper' for r in records))
        b.metric('Dataset candidates', sum(r['kind'] != 'Paper' for r in records))
        paper_tab, dataset_tab, review_tab, export_tab = st.tabs(['Papers', 'Datasets', 'Evidence review', 'Research brief'])
        for tab, papers in [(paper_tab, True), (dataset_tab, False)]:
            with tab:
                st.caption('Search snippets are unverified. Keyword match measures overlap, not evidence quality.')
                rows = [r for r in records if (r['kind'] == 'Paper') == papers]
                if not rows:
                    st.info('No results in this category.')
                for r in rows:
                    with st.container(border=True):
                        st.text(f"{r['id']} · {r['title']}")
                        st.caption(f"{r['kind']} · Keyword match: {r['keyword_match']}%")
                        st.text(r['snippet'] or 'No snippet supplied.')
                        if r['publication']:
                            st.text(r['publication'])
                        if r['accession_candidates']:
                            st.text('Unverified accessions: '+r['accession_candidates'])
                        if r['url']:
                            st.link_button('Open original source', r['url'])
        with review_tab:
            st.info('Read original sources before recording findings. Notes are user-entered, not AI-verified.')
            initial = [dict(Source=r['id']+' · '+r['title'], Reviewed=False, Methods='', Findings='', Limitations='')
                       for r in records if r['kind'] == 'Paper']
            notes = st.data_editor(initial, disabled=['Source'], hide_index=True,
                                   key=f"notes_{st.session_state.version}") if initial else []
        with export_tab:
            st.caption('Planning template; adapt only after verifying dataset suitability.')
            for i, step in enumerate(plan(bundle['resources']), 1):
                st.write(f'{i}. {step}')
            st.download_button('Download research brief', brief(bundle, notes), 'bioevidence_brief.md', 'text/markdown')
            st.download_button('Download results and notes', json.dumps({**bundle, 'review_notes': notes}, indent=2),
                               'bioevidence_results.json', 'application/json')
else:
    st.info('Enter a question and API key, or explore the clearly labelled synthetic demo.')
