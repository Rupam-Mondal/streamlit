import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Gym Manager", page_icon="🏋️", layout="centered")
st.title("🏋️ Gym Manager")
st.caption("A simple app to register gyms, add branches, and view gym details.")


def show_error(response: requests.Response):
    try:
        st.error(response.json().get("detail", "Something went wrong."))
    except ValueError:
        st.error("Could not reach the API. Make sure FastAPI is running.")


register_gym, register_branch, find_gym = st.tabs(
    ["Register Gym", "Register Branch", "View Gym"]
)

with register_gym:
    with st.form("gym_form", clear_on_submit=True):
        name = st.text_input("Gym name")
        owner_name = st.text_input("Owner name")
        phone = st.text_input("Phone")
        address = st.text_area("Address")
        submitted = st.form_submit_button("Register gym")
    if submitted:
        payload = {"name": name, "owner_name": owner_name, "phone": phone, "address": address}
        try:
            response = requests.post(f"{API_URL}/gyms", json=payload, timeout=10)
            if response.ok:
                st.success(f"Gym registered! Its ID is {response.json()['id']}.")
            else:
                show_error(response)
        except requests.RequestException:
            st.error("Could not reach the API. Make sure FastAPI is running.")

with register_branch:
    with st.form("branch_form", clear_on_submit=True):
        gym_id = st.number_input("Gym ID", min_value=1, step=1)
        branch_name = st.text_input("Branch name")
        branch_address = st.text_area("Branch address")
        city = st.text_input("City")
        submitted = st.form_submit_button("Register branch")
    if submitted:
        payload = {"gym_id": gym_id, "name": branch_name, "address": branch_address, "city": city}
        try:
            response = requests.post(f"{API_URL}/branches", json=payload, timeout=10)
            if response.ok:
                st.success("Branch registered successfully.")
            else:
                show_error(response)
        except requests.RequestException:
            st.error("Could not reach the API. Make sure FastAPI is running.")

with find_gym:
    gym_id = st.number_input("Enter gym ID", min_value=1, step=1, key="find_gym_id")
    if st.button("Get gym details"):
        try:
            response = requests.get(f"{API_URL}/gyms/{gym_id}", timeout=10)
            if response.ok:
                gym = response.json()
                st.subheader(gym["name"])
                st.write(f"**Owner:** {gym['owner_name']}")
                st.write(f"**Phone:** {gym['phone']}")
                st.write(f"**Address:** {gym['address']}")
                st.write("**Branches**")
                if gym["branches"]:
                    st.dataframe(gym["branches"], use_container_width=True, hide_index=True)
                else:
                    st.info("No branches registered yet.")
            else:
                show_error(response)
        except requests.RequestException:
            st.error("Could not reach the API. Make sure FastAPI is running.")
