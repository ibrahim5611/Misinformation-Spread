import streamlit as st
import requests

# Set your Google Fact Check API Key here
GOOGLE_API_KEY = "AIzaSyCVGG8uPZB4FRf0gIY7Hs2nFe_4k9RRgMY"

def google_fact_check(query):
    """Check misinformation using Google's Fact Check API"""
    url = f"https://factchecktools.googleapis.com/v1alpha1/claims:search?query={query}&key={GOOGLE_API_KEY}"
    
    response = requests.get(url)
    data = response.json()
    
    if "claims" in data and data["claims"]:
        fact_checks = data["claims"]
        result_text = ""
        total_score = 0  # Initialize risk score
        
        for claim in fact_checks[:3]:  # Show up to 3 fact-checks
            rating = claim["claimReview"][0].get("textualRating", "No Rating").lower()
            source = claim["claimReview"][0].get("publisher", {}).get("name", "Unknown")
            url = claim["claimReview"][0].get("url", "#")
            
            # Assign risk score based on credibility
            if "true" in rating or "correct" in rating:
                risk_score = 10  # Low risk
            elif "false" in rating or "incorrect" in rating:
                risk_score = 70  # Medium-High risk
            else:
                risk_score = 50  # Uncertain claim
            
            total_score += risk_score
            
            result_text += f"🔹 **Claim:** {claim.get('text', 'N/A')}\n"
            result_text += f"🔹 **Rating:** {rating.capitalize()}\n"
            result_text += f"🔹 **Source:** [{source}]({url})\n"
            result_text += f"🔹 **Assigned Risk Score:** {risk_score}/100\n\n"

        # Calculate final risk score (average)
        final_risk_score = total_score // len(fact_checks)
        
        return result_text, final_risk_score
    
    return "No fact-checking information available.", 90  # Default high-risk if no data found

# Streamlit UI
st.title("📰 Misinformation Detector with Risk Score")
st.write("Enter a news headline or statement to verify if it's real or misinformation.")

# User Input
user_input = st.text_area("Enter News/Statement:")
if st.button("Check"):
    if user_input:
        result, risk_score = google_fact_check(user_input)
        st.subheader("Fact-Check Results:")
        st.markdown(result)
        
        # Display Risk Score
        st.subheader(f"🛑 Misinformation Risk Score: {risk_score}/100")
        if risk_score <= 30:
            st.success("✅ Low Risk: Likely to be true.")
        elif risk_score <= 70:
            st.warning("⚠️ Medium Risk: Could be misleading.")
        else:
            st.error("🚨 High Risk: Likely misinformation!")

    else:
        st.warning("Please enter some text.")

st.sidebar.header("About")
st.sidebar.write("🚀 This app verifies misinformation using Google's Fact Check API and assigns a risk score.")
