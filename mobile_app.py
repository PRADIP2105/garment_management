import json
import os
from typing import Optional

import flet as ft
import requests

# Use environment variable or replace with your computer's IP address
API_BASE_URL = os.getenv("API_URL", "http://10.92.194.115:8000")


class ApiClient:
    def __init__(self) -> None:
        self.access_token: Optional[str] = None

    def set_token(self, token: str) -> None:
        self.access_token = token

    def _headers(self) -> dict:
        headers = {"Content-Type": "application/json"}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers

    def login(self, username: str, password: str) -> dict:
        url = f"{API_BASE_URL}/api/auth/token/"
        try:
            resp = requests.post(url, json={"username": username, "password": password}, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            self.set_token(data["access"])
            return data
        except requests.exceptions.ConnectionError:
            raise Exception(f"Could not connect to server at {API_BASE_URL}. Ensure the IP is correct and the server is running with '0.0.0.0'.")

    def get(self, path: str):
        url = f"{API_BASE_URL}{path}"
        resp = requests.get(url, headers=self._headers(), timeout=10)
        resp.raise_for_status()
        return resp.json()

    def register(self, username: str, password: str, email: str, company_name: str, company_address: str, company_city: str, company_mobile: str) -> dict:
        url = f"{API_BASE_URL}/api/auth/register/"
        try:
            resp = requests.post(url, json={
                "username": username,
                "password": password,
                "email": email,
                "company_name": company_name,
                "company_address": company_address,
                "company_city": company_city,
                "company_mobile": company_mobile
            }, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.ConnectionError:
            raise Exception(f"Could not connect to server at {API_BASE_URL}. Ensure the IP is correct and the server is running with '0.0.0.0'.")

    def register_view(self):
        page.controls.clear()

        reg_username = ft.TextField(label="Username", width=300)
        reg_password = ft.TextField(label="Password", password=True, can_reveal_password=True, width=300)
        reg_email = ft.TextField(label="Email", width=300)
        reg_company_name = ft.TextField(label="Company Name", width=300)
        reg_company_address = ft.TextField(label="Company Address", width=300)
        reg_company_city = ft.TextField(label="Company City", width=300)
        reg_company_mobile = ft.TextField(label="Company Mobile", width=300)

        def do_register(e):
            if not reg_username.value or not reg_password.value or not reg_email.value or not reg_company_name.value:
                show_snack("Please fill all required fields", color=ft.colors.ORANGE)
                return

            try:
                response = api.register(
                    reg_username.value,
                    reg_password.value,
                    reg_email.value,
                    reg_company_name.value,
                    reg_company_address.value,
                    reg_company_city.value,
                    reg_company_mobile.value
                )
                show_snack("Registration successful! Redirecting to Dashboard...", color=ft.colors.GREEN)
                page.go_to("/dashboard")  # Redirect to Dashboard instead of Create Account
                page.update()
            except Exception as ex:
                detail = str(ex)
                if hasattr(ex, 'response') and ex.response:
                    try:
                        detail = ex.response.json().get("detail", detail)
                    except:
                        pass
                show_snack(f"Registration failed: {detail}", color=ft.colors.RED)

        register_btn = ft.ElevatedButton("Register", on_click=do_register, width=300)

        page.add(
            ft.Column(
                [
                    ft.Text(
                        "Register New Account",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    reg_username,
                    reg_password,
                    reg_email,
                    reg_company_name,
                    reg_company_address,
                    reg_company_city,
                    reg_company_mobile,
                    register_btn,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=12,
            )
        )
        page.update()


# Define the actual page object and related functions
import flet as ft

# Initialize the Flet page object
page = ft.Page()

# Define the show_snack function
def show_snack(message, color):
    snack = ft.SnackBar(content=ft.Text(message), bgcolor=color)
    page.snack_bar = snack
    snack.open = True
    page.update()

# Define the login_view function
def login_view():
    page.controls.clear()
    # Navigate to the login page
    page.go_to("/login")  # Replace with the correct route for the login page
    page.update()

# Initialize the ApiClient instance
api = ApiClient()

def main():
    page.title = "Static Pages App"
    page.theme_mode = ft.ThemeMode.LIGHT

    # Define static pages
    def go_to_page1(e):
        page.controls.clear()
        page.add(ft.Text("This is Page 1"))
        page.add(ft.ElevatedButton("Go to Page 2", on_click=go_to_page2))
        page.update()

    def go_to_page2(e):
        page.controls.clear()
        page.add(ft.Text("This is Page 2"))
        page.add(ft.ElevatedButton("Go to Page 3", on_click=go_to_page3))
        page.update()

    def go_to_page3(e):
        page.controls.clear()
        page.add(ft.Text("This is Page 3"))
        page.add(ft.ElevatedButton("Go to Page 4", on_click=go_to_page4))
        page.update()

    def go_to_page4(e):
        page.controls.clear()
        page.add(ft.Text("This is Page 4"))
        page.add(ft.ElevatedButton("Go to Page 5", on_click=go_to_page5))
        page.update()

    def go_to_page5(e):
        page.controls.clear()
        page.add(ft.Text("This is Page 5"))
        page.add(ft.ElevatedButton("Go to Page 1", on_click=go_to_page1))
        page.update()

    # Start on Page 1
    go_to_page1(None)

if __name__ == "__main__":
    ft.app(target=main)
