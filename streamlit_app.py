from html import escape

import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Gym Manager", page_icon="GM", layout="wide")
st.markdown(
    """
    <style>
      .block-container { max-width: 1120px; padding-top: 2.4rem; padding-bottom: 3rem; }
      [data-testid="stAppViewContainer"] { background: #f7f8fc; }
      .hero { background: linear-gradient(120deg, #172554, #2563eb); border-radius: 18px; padding: 28px 32px; color: white; margin-bottom: 24px; }
      .hero h1 { margin: 0; font-size: 2rem; } .hero p { margin: 7px 0 0; opacity: .82; }
      .label { color: #64748b; font-size: .82rem; margin-bottom: 3px; } .value { color: #172554; font-weight: 600; font-size: 1rem; }
      .branch-card { background: white; border: 1px solid #e2e8f0; border-radius: 14px; padding: 18px; min-height: 136px; box-shadow: 0 2px 5px rgba(15,23,42,.03); }
      .branch-card h4 { color: #172554; margin: 0 0 10px; } .branch-card p { color: #64748b; margin: 4px 0; font-size: .92rem; }
      div[data-testid="stMetric"] { background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 10px 16px; }
      .stButton > button { border-radius: 8px; font-weight: 600; }
    </style>
    """,
    unsafe_allow_html=True,
)


def api_error(response: requests.Response) -> str:
    try:
        return response.json().get("detail", "Something went wrong. Please try again.")
    except ValueError:
        return "Could not reach the API. Make sure FastAPI is running."


def get_gyms():
    try:
        response = requests.get(f"{API_URL}/gyms", timeout=5)
        if response.ok:
            return response.json(), None
        return [], api_error(response)
    except requests.RequestException:
        return [], "Could not reach the API. Start FastAPI, then refresh this page."


def get_gym(gym_id: int):
    try:
        response = requests.get(f"{API_URL}/gyms/{gym_id}", timeout=5)
        if response.ok:
            return response.json(), None
        return None, api_error(response)
    except requests.RequestException:
        return None, "Could not reach the API. Make sure FastAPI is running."


st.markdown('<div class="hero"><h1>Gym Manager</h1><p>Manage your gyms and branch locations in one simple place.</p></div>', unsafe_allow_html=True)
gyms, load_error = get_gyms()
if load_error:
    st.warning(load_error)

total_branches = sum(len(gym.get("branches", [])) for gym in gyms)
metric_one, metric_two, metric_three = st.columns(3)
metric_one.metric("Registered gyms", len(gyms))
metric_two.metric("Total branches", total_branches)
metric_three.metric("Status", "Ready" if not load_error else "API offline")

st.divider()
directory_tab, add_gym_tab, add_branch_tab = st.tabs(["Gym directory", "Add gym", "Add branch"])

with directory_tab:
    if not gyms:
        st.info("No gyms yet. Add your first gym from the **Add gym** tab.")
    else:
        gym_lookup = {f"{gym['name']}  (#{gym['id']})": gym["id"] for gym in gyms}
        selection = st.selectbox("Choose a gym", list(gym_lookup), label_visibility="collapsed")
        selected_gym, detail_error = get_gym(gym_lookup[selection])
        if detail_error:
            st.error(detail_error)
        elif selected_gym:
            st.subheader(selected_gym["name"])
            owner, phone, address = st.columns([1, 1, 2])
            owner.markdown(f'<div class="label">OWNER</div><div class="value">{escape(selected_gym["owner_name"])}</div>', unsafe_allow_html=True)
            phone.markdown(f'<div class="label">PHONE</div><div class="value">{escape(selected_gym["phone"])}</div>', unsafe_allow_html=True)
            address.markdown(f'<div class="label">MAIN ADDRESS</div><div class="value">{escape(selected_gym["address"])}</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"#### Branches ({len(selected_gym['branches'])})")
            if not selected_gym["branches"]:
                st.info("No branches have been added to this gym yet.")
            else:
                for start in range(0, len(selected_gym["branches"]), 3):
                    columns = st.columns(3)
                    for column, branch in zip(columns, selected_gym["branches"][start : start + 3]):
                        with column:
                            st.markdown(
                                f'''<div class="branch-card"><h4>{escape(branch["name"])}</h4><p><b>City</b> &middot; {escape(branch["city"])}</p><p>{escape(branch["address"])}</p></div>''',
                                unsafe_allow_html=True,
                            )

with add_gym_tab:
    st.write("Add the main details for a gym.")
    with st.form("gym_form", clear_on_submit=True):
        left, right = st.columns(2)
        with left:
            name = st.text_input("Gym name", placeholder="e.g. Peak Fitness")
            owner_name = st.text_input("Owner name", placeholder="e.g. Rahul Sharma")
        with right:
            phone = st.text_input("Phone number", placeholder="e.g. +91 98765 43210")
            address = st.text_input("Main address", placeholder="Street, area, city")
        submitted = st.form_submit_button("Save gym", use_container_width=True)
    if submitted:
        payload = {"name": name, "owner_name": owner_name, "phone": phone, "address": address}
        try:
            response = requests.post(f"{API_URL}/gyms", json=payload, timeout=10)
            if response.ok:
                st.success(f"{response.json()['name']} was added successfully.")
                st.rerun()
            else:
                st.error(api_error(response))
        except requests.RequestException:
            st.error("Could not reach the API. Make sure FastAPI is running.")

with add_branch_tab:
    if not gyms:
        st.info("Add a gym first, then you can add its branch locations here.")
    else:
        st.write("Add a branch to an existing gym.")
        with st.form("branch_form", clear_on_submit=True):
            branch_gym = st.selectbox("Gym", gyms, format_func=lambda gym: gym["name"])
            left, right = st.columns(2)
            with left:
                branch_name = st.text_input("Branch name", placeholder="e.g. Indiranagar Branch")
                city = st.text_input("City", placeholder="e.g. Bengaluru")
            with right:
                branch_address = st.text_input("Branch address", placeholder="Street, area")
            submitted = st.form_submit_button("Save branch", use_container_width=True)
        if submitted:
            payload = {"gym_id": branch_gym["id"], "name": branch_name, "address": branch_address, "city": city}
            try:
                response = requests.post(f"{API_URL}/branches", json=payload, timeout=10)
                if response.ok:
                    st.success(f"{response.json()['name']} was added successfully.")
                    st.rerun()
                else:
                    st.error(api_error(response))
            except requests.RequestException:
                st.error("Could not reach the API. Make sure FastAPI is running.")
