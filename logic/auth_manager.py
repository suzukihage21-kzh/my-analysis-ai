import os
import streamlit as st
import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build

class AuthManager:
    def __init__(self):
        self.client_config = self._get_client_config()
        self.scopes = [
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile",
            "openid",
        ]
        # Redirect URI setting
        # Local: http://localhost:8501
        # Cloud: https://[your-app].streamlit.app
        # We try to detect or expect it in secrets, default to localhost for dev
        self.redirect_uri = self._get_redirect_uri()

    def _get_client_config(self):
        """
        Get client config from Streamlit secrets or environment variables.
        Expected structure in secrets:
        [google_auth]
        client_id = "..."
        client_secret = "..."
        project_id = "..."
        auth_uri = "https://accounts.google.com/o/oauth2/auth"
        token_uri = "https://oauth2.googleapis.com/token"
        """
        if hasattr(st, "secrets") and "google_auth" in st.secrets:
            return {
                "web": {
                    "client_id": st.secrets["google_auth"]["client_id"],
                    "project_id": st.secrets["google_auth"]["project_id"],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_secret": st.secrets["google_auth"]["client_secret"],
                    "redirect_uris": [self._get_redirect_uri()],
                }
            }
        return None

    def _get_redirect_uri(self):
        # Allow overriding via secrets for Cloud deployment
        if hasattr(st, "secrets") and "google_auth" in st.secrets and "redirect_uri" in st.secrets["google_auth"]:
            return st.secrets["google_auth"]["redirect_uri"]
        return "http://localhost:8501"

    def get_auth_url(self):
        """Generate the authorization URL."""
        if not self.client_config:
            return None
        
        flow = google_auth_oauthlib.flow.Flow.from_client_config(
            self.client_config,
            scopes=self.scopes,
            redirect_uri=self.redirect_uri
        )
        authorization_url, state = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true"
        )
        # Store state in session to verify callback
        st.session_state["google_auth_state"] = state
        return authorization_url

    def get_token_from_code(self, code):
        """Exchange the auth code for a token."""
        if not self.client_config:
            return None

        flow = google_auth_oauthlib.flow.Flow.from_client_config(
            self.client_config,
            scopes=self.scopes,
            redirect_uri=self.redirect_uri,
            state=st.session_state.get("google_auth_state")
        )
        flow.fetch_token(code=code)
        return flow.credentials

    def get_user_info(self, credentials):
        """Get user info from Google API."""
        try:
            service = build("oauth2", "v2", credentials=credentials)
            user_info = service.userinfo().get().execute()
            return user_info
        except Exception as e:
            st.error(f"Failed to fetch user info: {e}")
            return None

    def is_configured(self):
        return self.client_config is not None
