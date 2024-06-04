import streamlit as st
import stripe
import os
import json

# Load Stripe secret key and base URL from secrets.toml
stripe.api_key = st.secrets["stripe"]["secret_key"]
base_url = st.secrets["urls"]["base_url"]

def create_checkout_session(amount, currency):
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': currency,
                    'product_data': {
                        'name': 'Résultat du questionnaire TSA',
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
        st.error(f"Erreur lors de la création de la session de paiement: {e}")
        return None

def questionnaire_page():
    st.title('Questionnaire TSA')

    questions = [
        "Avez-vous du mal à comprendre les sentiments des autres ?",
        "Remarquez-vous souvent de petits sons que les autres ne remarquent pas ?",
        "Préférez-vous faire les choses de la même manière encore et encore ?",
        "Avez-vous du mal à établir un contact visuel lorsque vous parlez aux gens ?",
        "Aimez-vous collectionner des objets ou des informations sur des sujets spécifiques ?",
        "Avez-vous du mal à suivre une conversation lorsqu'il y a du bruit autour de vous ?",
        "Avez-vous des difficultés à comprendre les expressions idiomatiques ou les sarcasmes ?",
        "Avez-vous besoin de routines et de planification pour vous sentir à l'aise ?",
        "Avez-vous des intérêts particuliers qui prennent beaucoup de votre temps et de votre attention ?",
        "Avez-vous du mal à interpréter les gestes et les expressions faciales des autres ?",
    ]

    responses = []
    for question in questions:
        response = st.selectbox(question, ['Tout à fait d’accord', 'D’accord', 'Neutre', 'Pas d’accord', 'Pas du tout d’accord'])
        responses.append(response)

    if st.button('Soumettre', key='submit'):
        st.session_state['responses'] = responses
        st.write("### Vos réponses ont été enregistrées.")
        st.write("### Pour télécharger votre résultat, veuillez procéder au paiement.")

        # Store responses in a temporary file
        with open("temp_responses.json", "w") as f:
            json.dump(responses, f)

        session = create_checkout_session(500, 'eur')  # 500 cents = 5 euros
        if session:
            st.markdown(f"""
            <a href="{session.url}" target="_blank">
                <button style="background-color:#4CAF50; color:white; padding: 10px 20px; border: none; cursor: pointer;">
                    Aller au paiement
                </button>
            </a>
            """, unsafe_allow_html=True)
        else:
            os.remove("temp_responses.json")  # Remove the temporary file if checkout session creation fails
            st.error("Échec de la création d'une session de paiement")

def success_page():
    st.title("Paiement réussi")
    st.write("Merci pour votre paiement. Vous pouvez maintenant télécharger votre résultat.")

    if os.path.exists("temp_responses.json"):
        # Load responses from the temporary file
        with open("temp_responses.json", "r") as f:
            responses = json.load(f)
        st.session_state['responses'] = responses

        # Generate and offer the result download (for demonstration, we use a text file)
        result_content = "Votre résultat du questionnaire TSA:\n\n" + "\n".join(responses)
        result_file = "result.txt"
        with open(result_file, 'w') as f:
            f.write(result_content)
        with open(result_file, 'rb') as f:
            st.download_button(
                label="Télécharger le résultat",
                data=f,
                file_name="Resultat_TSA.txt",
                mime="text/plain",
            )
        os.remove(result_file)
        os.remove("temp_responses.json")  # Remove the temporary file after successful download
    else:
        st.write("Aucune réponse à afficher.")

def cancel_page():
    st.title("Paiement annulé")
    st.write("Votre paiement a été annulé. Veuillez réessayer.")

    if os.path.exists("temp_responses.json"):
        os.remove("temp_responses.json")  # Remove the temporary file if payment is canceled

def main():
    st.set_page_config(page_title="Questionnaire TSA", page_icon=":brain:", layout="wide")

    if 'responses' not in st.session_state:
        st.session_state['responses'] = []

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
