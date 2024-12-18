import streamlit as st
import re
from openai import OpenAI
from pathlib import Path


def extract_urls(text):
    """
    Extract URLs from the given text and convert them to hyperlinks.

    Args:
        text (str): Input text containing potential URLs

    Returns:
        str: Text with URLs converted to markdown hyperlinks
    """
    url_pattern = r'https?://\S+'

    def replace_url(match):
        url = match.group(0)
        return f'[{url}]({url})'

    return re.sub(url_pattern, replace_url, text)


def setup_page_config():
    """Configure Streamlit page settings with enhanced styling."""
    icon_path = Path("icon.png")  # Replace with the actual file path

    # Set up the page configuration
    st.set_page_config(
        page_title="Scholar Seeker",
        page_icon=str(icon_path),
        layout="centered",
        initial_sidebar_state="expanded"
    )

    # Custom CSS for enhanced styling
    st.markdown("""
    <style>
    /* General app background and font settings */
    .stApp {
        background-color: #f9fafb; /* Light gray for a clean background */
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* Header styling for the main title */
    .main-header {
        font-size: 2.5em;
        font-weight: bold;
        color: #1E88E5; /* Primary blue color */
        text-align: center;
        margin-bottom: 30px;
    }

    .st-bx{
    max-height:100px;
    }

    /* Chat box styling */
    .stChatMessage {
        background-color: white; /* Neutral white for contrast */
        border-radius: 12px; /* Rounded corners for better UI */
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1); /* Subtle shadow for depth */
    }

    /* User messages with green styling */
    .stChatMessage.user {
        border-left: 5px solid #43A047; /* Green accent */
        background-color: #e8f5e9; /* Light green background */
    }

    /* Assistant messages with blue styling */
    .stChatMessage.assistant {
        border-left: 5px solid #1E88E5; /* Blue accent */
        background-color: #e3f2fd; /* Light blue background */
    }

    /* Sidebar styling */
    .stSidebar {
        background-color: #ffffff; /* Clean white sidebar */
        box-shadow: 2px 0 5px rgba(0, 0, 0, 0.1); /* Subtle shadow */
    }

    /* Text input field styling */
    .stTextInput > div > div > input {
        background-color: #f9fafb;
        border: 1px solid #cccccc; /* Light border for contrast */
        padding: 10px;
        color: #333333;
    }

    /* Footer styling */
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #f1f1f1;
        color: #666666;
        text-align: center;
        padding: 10px;
        font-size: 0.9em;
    }
    .st-emotion-cache-arzcut  {
        background-color: #f9fafb;
      }
    .st-emotion-cache-128upt6{
          background-color: #f9fafb;

      }

    .st-emotion-cache-a4s44t{
     background-color: #f9fafb;

    }
    .loading-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(255, 255, 255, 0.8);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1000;
        font-size: 1.5em;
        color: #1E88E5;
    }
    </style>
    """, unsafe_allow_html=True)


def convert_image_to_base64(image_path):
    """
    Convert an image to a base64 string for embedding.

    Args:
        image_path (str): Path to the image file.

    Returns:
        str: Base64 encoded string of the image.
    """
    import base64
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def api_key_sidebar():
    """
    Create sidebar for API key input with enhanced UI.
    Returns:
        str: Perplexity API key
    """
    # Make sidebar a flex container with full viewport height
    st.markdown("""
    <style>
    [data-testid="stSidebar"] > div:first-child {
        display: flex;
        flex-direction: column;
        height: 100vh;
    }
    </style>
    """, unsafe_allow_html=True)

    icon_path = "icon.png"  # Replace with the actual file path

    with st.sidebar:
        st.markdown(
            f"""
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center;">
                <img src="data:image/png;base64,{convert_image_to_base64(icon_path)}" style="width: 100px; margin-bottom: 10px;">
                <h3>Scholar Seeker</h3>
                <p style="font-size: 14px;">Research Companion for Scholarly Exploration</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        api_key = st.secrets['OPENAI_API_KEY']


        st.markdown("---")
        st.info("💡 Tip: Ask specific, well-defined scholarships questions for best results.")

        # Add a flexible spacer to push the button towards the bottom
        st.markdown("<div style='flex:1;'></div>", unsafe_allow_html=True)

        # Button at the bottom
        st.markdown(
            """
            <div style="text-align:center; margin-top:156px;">
                <a href="https://forms.gle/MzK9XjhgzqTSUk1f6" target="_blank" style="text-decoration:none;">
                    <button 
                        style="
                            background-color:rgb(74 122 165); 
                            color:white; 
                            padding:10px 20px; 
                            border:none; 
                            border-radius:4px; 
                            cursor:pointer; 
                            font-size:16px; 
                            font-weight:bold; 
                            box-shadow:0 2px 5px rgba(0, 0, 0, 0.1);
                            transition: background-color 0.3s ease, box-shadow 0.3s ease;
                        "
                        onmouseover="this.style.backgroundColor='#1769AA';this.style.boxShadow='0 4px 10px rgba(0,0,0,0.1)';"
                        onmouseout="this.style.backgroundColor='rgb(74 122 165)';this.style.boxShadow='0 2px 5px rgba(0,0,0,0.1)';"
                    >
                        💬 Share Feedback
                    </button>
                </a>
            </div>
            """,
            unsafe_allow_html=True
        )

    return api_key


def initialize_chat_history():
    """
    Initialize or retrieve chat session state.

    Returns:
        list: Chat messages
    """
    if "messages" not in st.session_state:
        st.session_state.messages = []
    return st.session_state.messages


def replace_citation_markers(text, citations):
    """
    Replace citation markers like [1], [2] in the text with hyperlinks to the citations.

    Args:
        text (str): The assistant's response containing citation markers.
        citations (list): List of citation URLs.

    Returns:
        str: Text with citation markers replaced by hyperlinks.
    """

    def replace_marker(match):
        marker = match.group(0)
        index = int(match.group(1)) - 1  # Adjust for zero-based index
        if 0 <= index < len(citations):
            url = citations[index]
            return f'<a href="{url}" target="_blank">{marker}</a>'
        else:
            return marker  # Leave the marker as is if index is out of range

    # Regex pattern to find citation markers like [1], [2], etc.
    pattern = r'\[(\d+)\]'

    # Replace markers with hyperlinks
    return re.sub(pattern, replace_marker, text)


def display_chat_history(messages):
    """
    Display previous chat messages with user and assistant styling.

    Args:
        messages (list): List of chat messages
    """
    # Path to the assistant avatar icon
    assistant_avatar = "icon.png"  # Replace with the actual path to your icon file

    for message in messages:
        # Determine avatar based on the role
        if message["role"] == "user":
            avatar = "🧑"  # Emoji avatar for user
        elif message["role"] == "assistant":
            # Use assistant avatar image if it exists, fallback to emoji
            avatar = assistant_avatar if Path(assistant_avatar).is_file() else "🎓"
        else:
            avatar = None  # No avatar for system messages

        with st.chat_message(message["role"], avatar=avatar):
            # Convert URLs to hyperlinks
            content_with_links = extract_urls(message["content"])
            st.markdown(content_with_links, unsafe_allow_html=True)


def generate_assistant_response(client, messages):
    """
    Generate AI-powered research response using Perplexity API.

    Args:
        client (OpenAI): Configured OpenAI/Perplexity client
        messages (list): Chat message history

    Returns:
        str: Generated research response
    """
    # Predefined system prompt for scholarly research assistant
    api_messages = [
        {
            "role": "system",
            "content": """You are Scholar Seeker, a specialized AI assistant that ONLY provides information about scholarships. You must reject all other queries, regardless of their nature.
            STRICT RESPONSE PROTOCOL:
            "CRITICAL: You MUST ONLY respond to queries explicitly about scholarships. For ANY other topic, reply ONLY with: 'I exclusively provide scholarship information. Please ask a scholarship-related question.'"
            1. Query Validation
                - Immediately assess if query is scholarship-related
                -Immediately reject if query is non-scholarship based
            2. Scholarship Information Scope:
                ONLY provide information about:
                - Scholarship eligibility
                - Application requirements
                - Award amounts
                - Deadlines
                - Application processes
                - Documentation needs
                - Scholarship-specific contact information
            3. Automatic Query Rejection Categories:
                Immediately reject queries about:
                - Any non-scholarship topic
            4. Valid Scholarship Query Response Structure:
                When providing scholarship information:
                - Scholarship Name
                - Provider Details
                - Award Amount
                - Eligibility Criteria
                - Application Requirements
                - Important Dates
                - Official Contact Information
                - Verification Source
            5. Verification Requirements:
                For all scholarship information:
                - Include last verification date
                - Official source link
                - Current status (active/inactive)
                - Administrator contact details
            6. Mandatory Disclaimer:
                Include with all scholarship information:
                "This information is for reference only. Verify all details through official scholarship sources. Requirements and deadlines may change."
            7. Query Handling Protocol:
                Step 1: Assess if query is STRICTLY about scholarships
                Step 2: If NO - provide rejection response
                Step 3: If YES - request necessary details:
                    - Academic level
                    - Field of study
                    - Geographic eligibility
                    - Citizenship status
                Step 4: Provide structured scholarship information
            8. Zero Tolerance Policy:
                - No exceptions for non-scholarship queries
                - No partial answers to mixed queries
                - No general advice even if education-related
                - No referrals to other services
                - No engagement in general discussion
            Remember: You are ONLY a scholarship information system. Maintain absolute focus on scholarship-related queries and reject everything else immediately and firmly."""
        }
    ]

    api_messages += [
        {"role": m["role"], "content": m["content"]} for m in messages
    ]

    try:
        response_stream = client.chat.completions.create(
            model="llama-3.1-sonar-large-128k-online",
            messages=api_messages,
            stream=True
        )

        full_response = ""
        message_placeholder = st.empty()
        citations = []  # Initialize citations list

        for chunk in response_stream:
            # Collect citations if available
            if hasattr(chunk, 'citations') and chunk.citations:
                citations.extend(chunk.citations)

            # Build the full response text
            if chunk.choices[0].delta.content is not None:
                full_response += chunk.choices[0].delta.content
                message_placeholder.markdown(full_response + "▌")

        # After receiving the full response
        message_placeholder.markdown(full_response)

        # Replace citation markers with hyperlinks
        content_with_links = replace_citation_markers(full_response, citations)
        message_placeholder.markdown(content_with_links, unsafe_allow_html=True)

        # Store citations in session state
        st.session_state['last_citations'] = citations

        return full_response

    except Exception as e:
        st.error(f"Research query error: {e}")
        return "Apologies, an error occurred during research retrieval."


def main():
    """
    Main Streamlit application workflow.
    """
    # Setup page configuration
    setup_page_config()

    # Initialize response generation flag
    if 'generating_response' not in st.session_state:
        st.session_state.generating_response = False

    # Display main header
    # Display combined header and subtext with vibrant blue header

    st.markdown(
        '''
        <div style="text-align: center;">
            <h1 style="color: #007BFF; margin-bottom: 5px;">Scholar Seeker</h1>
            <p style="color: #555555; margin-top: 0px;">Bridging financial gap between ambition and education.</p>
        </div>
        ''',
        unsafe_allow_html=True
    )

    # Retrieve API key
    api_key = api_key_sidebar()

    if not api_key:
        st.warning('Please enter your API key to proceed.')
        return

    # Initialize OpenAI client with Perplexity API
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.perplexity.ai"
    )

    # Initialize chat history
    messages = initialize_chat_history()

    # Display previous chat messages
    display_chat_history(messages)

    # User input handling
    if not st.session_state.generating_response:
        prompt = st.chat_input("Type your scholarship question here...")
        if prompt:
            # Set the flag to prevent new queries
            st.session_state.generating_response = True

            # Append user message to history
            messages.append({"role": "user", "content": prompt})

            # Display user message
            with st.chat_message("user", avatar='🧑'):
                st.markdown(prompt)

                # # Display loading overlay
                # loading_placeholder = st.empty()
                # loading_placeholder.markdown(
                #     '<div class="loading-overlay">Generating response...</div>',
                #     unsafe_allow_html=True
                # )

                # Generate and display assistant response
            icon_path = "icon.png"  # Replace with the correct file path

            with st.chat_message("assistant", avatar=icon_path):
                full_response = generate_assistant_response(client, messages)

                # Append assistant response to history
                messages.append({"role": "assistant", "content": full_response})
                #
                # # Remove loading overlay
                # loading_placeholder.empty()
                #
                # # Reset the flag to allow new queries
            st.session_state.generating_response = False
    else:
        # If a response is being generated, show a disabled chat input
        st.chat_input("Please wait for the current response...", disabled=True)

        # Footer note
    st.markdown('<div class="footer">© 2024 Scholar Seeker. All rights reserved.</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
