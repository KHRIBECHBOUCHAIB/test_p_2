import streamlit as st
import stripe
import os

# Load Stripe secret key and base URL from secrets.toml
stripe.api_key = st.secrets["stripe"]["secret_key"]
base_url = st.secrets["urls"]["base_url"]

# Function to create a checkout session
def create_checkout_session(amount, currency):
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': currency,
                    'product_data': {
                        'name': 'TSA Questionnaire Result',
                    },
                    'unit_amount': amount,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f'{base_url}?page=success',
            cancel_url=f'{base_url}?page=cancel',
        )
        return session
    except Exception as e:
        st.error(f"Error creating checkout session: {e}")
        return None

# Page for the questionnaire
def questionnaire_page():
    st.title('TSA Questionnaire')

    questions = [
        "Do you find it difficult to understand people’s feelings?",
        "Do you often notice small sounds when others do not?",
        "Do you prefer to do things the same way over and over again?",
    ]

    responses = []
    for question in questions:
        response = st.radio(question, ['Yes', 'No'])
        responses.append(response)

    if st.button('Submit'):
        st.session_state['responses'] = responses
        st.write("### Your responses have been recorded.")
        st.write("### To download your result, please proceed to payment.")
        session = create_checkout_session(500, 'eur')  # 500 cents = 5 euros
        if session:
            st.write("### Redirecting to Stripe Checkout...")
            st.write(session.url)
            st.markdown(f"""
            <a href="{session.url}" target="_blank">
                <button style="background-color:#4CAF50; color:white; padding: 10px 20px; border: none; cursor: pointer;">
                    Go to Checkout
                </button>
            </a>
            """, unsafe_allow_html=True)
        else:
            st.error("Failed to create a checkout session")

# Page for the success URL
def success_page():
    st.title("Payment Successful")
    st.write("Thank you for your payment. You can now download your result.")

    if 'responses' in st.session_state:
        # Generate and offer the result download (for demonstration, we use a text file)
        result_content = "Your TSA Questionnaire Result:\n\n" + "\n".join(st.session_state.get('responses', []))
        result_file = "result.txt"
        with open(result_file, 'w') as f:
            f.write(result_content)
        with open(result_file, 'rb') as f:
            st.download_button(
                label="Download Result",
                data=f,
                file_name="TSA_Result.txt",
                mime="text/plain",
            )
        os.remove(result_file)
    else:
        st.write("No responses to display.")

# Page for the cancel URL
def cancel_page():
    st.title("Payment Cancelled")
    st.write("Your payment was cancelled. Please try again.")

# Main app logic
def main():
    if 'responses' not in st.session_state:
        st.session_state['responses'] = []

    # Update query parameter handling to use st.experimental_get_query_params
    query_params = st.experimental_get_query_params()
    page = query_params.get("page", ["questionnaire"])[0]

    if page == "questionnaire":
        questionnaire_page()
    elif page == "success":
        success_page()
    elif page == "cancel":
        cancel_page()

if __name__ == "__main__":
    main()
