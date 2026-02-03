import flet as ft
import requests
import json
from datetime import datetime, date


class GarmentApp:
    def __init__(self):
        self.base_url = "http://10.92.194.47:8000/api"  # Use your computer's IP
        self.access_token = None
        self.user_data = None
        
    def create_bottom_nav(self, page, selected_index):
        """Create bottom navigation bar"""
        return ft.NavigationBar(
            destinations=[
                ft.NavigationDestination(icon=ft.icons.DASHBOARD, label="Dashboard"),
                ft.NavigationDestination(icon=ft.icons.PEOPLE, label="Workers"),
                ft.NavigationDestination(icon=ft.icons.BUSINESS, label="Suppliers"),
                ft.NavigationDestination(icon=ft.icons.INVENTORY, label="Materials"),
                ft.NavigationDestination(icon=ft.icons.STORE, label="Stock"),
                ft.NavigationDestination(icon=ft.icons.WORK, label="Work"),
            ],
            selected_index=selected_index,
            on_change=lambda e: self.bottom_nav_change(page, e)
        )
    
    def bottom_nav_change(self, page, e):
        """Handle bottom navigation change"""
        routes = ["/dashboard", "/workers", "/suppliers", "/materials", "/stock", "/work_distribution"]
        if e.control.selected_index < len(routes):
            page.go(routes[e.control.selected_index])
    
    def create_drawer(self, page):
        """Create navigation drawer"""
        return ft.NavigationDrawer(
            controls=[
                ft.Container(height=20),
                ft.NavigationDrawerDestination(
                    label="Dashboard",
                    icon=ft.icons.DASHBOARD,
                    selected_icon=ft.icons.DASHBOARD_OUTLINED
                ),
                ft.NavigationDrawerDestination(
                    label="Workers",
                    icon=ft.icons.PEOPLE,
                    selected_icon=ft.icons.PEOPLE_OUTLINED
                ),
                ft.NavigationDrawerDestination(
                    label="Suppliers", 
                    icon=ft.icons.BUSINESS,
                    selected_icon=ft.icons.BUSINESS_OUTLINED
                ),
                ft.NavigationDrawerDestination(
                    label="Materials",
                    icon=ft.icons.INVENTORY,
                    selected_icon=ft.icons.INVENTORY_OUTLINED
                ),
                ft.NavigationDrawerDestination(
                    label="Stock",
                    icon=ft.icons.STORE,
                    selected_icon=ft.icons.STORE_OUTLINED
                ),
                ft.NavigationDrawerDestination(
                    label="Work Distribution",
                    icon=ft.icons.WORK,
                    selected_icon=ft.icons.WORK_OUTLINED
                ),
                ft.Divider(),
                ft.NavigationDrawerDestination(
                    label="Logout",
                    icon=ft.icons.LOGOUT
                ),
            ],
            on_change=lambda e: self.drawer_change(page, e)
        )
    
    def drawer_change(self, page, e):
        """Handle drawer navigation"""
        index = e.control.selected_index
        routes = ["/dashboard", "/workers", "/suppliers", "/materials", "/stock", "/work_distribution"]
        if index < len(routes):
            page.go(routes[index])
        elif index == 6:  # Logout
            self.logout(page)
        page.drawer.open = False
        page.update()
    
    def show_navigation_menu(self, page):
        """Show navigation menu dialog"""
        dlg = ft.AlertDialog(
            modal=False,
            title=ft.Text("Navigation"),
            content=ft.Container(
                content=ft.Column([
                    ft.ElevatedButton("Dashboard", on_click=lambda _: self.navigate_to(page, "/dashboard")),
                    ft.ElevatedButton("Workers", on_click=lambda _: self.navigate_to(page, "/workers")),
                    ft.ElevatedButton("Suppliers", on_click=lambda _: self.navigate_to(page, "/suppliers")),
                    ft.ElevatedButton("Materials", on_click=lambda _: self.navigate_to(page, "/materials")),
                    ft.ElevatedButton("Stock", on_click=lambda _: self.navigate_to(page, "/stock")),
                    ft.ElevatedButton("Work Distribution", on_click=lambda _: self.navigate_to(page, "/work_distribution")),
                    ft.ElevatedButton("Logout", on_click=lambda _: self.logout(page), bgcolor=ft.colors.RED, color=ft.colors.WHITE),
                ], tight=True),
                width=250,
                height=300
            ),
        )
        
        page.dialog = dlg
        dlg.open = True
        page.update()
    
    def create_bottom_nav(self, page, selected_index=0):
        """Create bottom navigation bar"""
        return ft.NavigationBar(
            destinations=[
                ft.NavigationDestination(icon=ft.icons.DASHBOARD, label="Dashboard"),
                ft.NavigationDestination(icon=ft.icons.PEOPLE, label="Workers"),
                ft.NavigationDestination(icon=ft.icons.BUSINESS, label="Suppliers"),
                ft.NavigationDestination(icon=ft.icons.INVENTORY, label="Materials"),
                ft.NavigationDestination(icon=ft.icons.STORE, label="Stock"),
                ft.NavigationDestination(icon=ft.icons.WORK, label="Work"),
            ],
            on_change=lambda e: self.bottom_nav_change(page, e),
            selected_index=selected_index
        )
    
    def bottom_nav_change(self, page, e):
        """Handle bottom navigation change"""
        routes = ["/dashboard", "/workers", "/suppliers", "/materials", "/stock", "/work_distribution"]
        if e.control.selected_index < len(routes):
            page.go(routes[e.control.selected_index])
    
    def main(self, page: ft.Page):
        page.title = "Garment Management System"
        page.theme_mode = ft.ThemeMode.LIGHT
        
        # Navigation
        def route_change(route):
            page.views.clear()
            
            if page.route == "/":
                page.views.append(self.login_view(page))
            elif page.route == "/dashboard":
                page.views.append(self.dashboard_view(page))
            elif page.route == "/workers":
                page.views.append(self.workers_view(page))
            elif page.route == "/suppliers":
                page.views.append(self.suppliers_view(page))
            elif page.route == "/materials":
                page.views.append(self.materials_view(page))
            elif page.route == "/stock":
                page.views.append(self.stock_view(page))
            elif page.route == "/work_distribution":
                page.views.append(self.work_distribution_view(page))
            elif page.route == "/work_return":
                page.views.append(self.work_return_view(page))
            
            page.update()
        
        page.on_route_change = route_change
        page.go("/")
    
    def login_view(self, page):
        username_field = ft.TextField(
            label="Username", 
            width=300,
            value="logintest"  # Pre-filled for testing
        )
        password_field = ft.TextField(
            label="Password", 
            password=True, 
            width=300,
            value="password123"  # Pre-filled for testing
        )
        status_text = ft.Text("Enter your credentials", color=ft.colors.BLUE)
        
        def login_click(e):
            if not username_field.value or not password_field.value:
                status_text.value = "Please fill all fields"
                status_text.color = ft.colors.RED
                page.update()
                return
            
            status_text.value = "Logging in..."
            status_text.color = ft.colors.BLUE
            page.update()
            
            try:
                response = requests.post(f"{self.base_url}/auth/login/", {
                    "username": username_field.value,
                    "password": password_field.value
                })
                
                if response.status_code == 200:
                    data = response.json()
                    self.access_token = data['tokens']['access']
                    self.user_data = data['user']
                    status_text.value = "Login successful!"
                    status_text.color = ft.colors.GREEN
                    page.update()
                    page.go("/dashboard")
                else:
                    status_text.value = "Invalid credentials"
                    status_text.color = ft.colors.RED
                    page.update()
            except Exception as e:
                status_text.value = f"Error: {str(e)}"
                status_text.color = ft.colors.RED
                page.update()
        
        return ft.View(
            "/",
            [
                ft.AppBar(title=ft.Text("Login"), bgcolor=ft.colors.BLUE),
                ft.Column([
                    ft.Container(height=20),
                    ft.Text("Garment Management System", 
                           size=24, 
                           weight=ft.FontWeight.BOLD,
                           text_align=ft.TextAlign.CENTER),
                    ft.Container(height=30),
                    status_text,
                    ft.Container(height=20),
                    username_field,
                    password_field,
                    ft.Container(height=20),
                    ft.ElevatedButton(
                        "Login", 
                        on_click=login_click, 
                        width=300,
                        bgcolor=ft.colors.BLUE,
                        color=ft.colors.WHITE
                    ),
                ], 
                alignment=ft.MainAxisAlignment.CENTER, 
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                scroll=ft.ScrollMode.AUTO)
            ]
        )
    
    def dashboard_view(self, page):
        if not self.access_token:
            page.go("/")
            return
        
        # Dashboard stats container
        stats_container = ft.Container(
            content=ft.Text("Loading dashboard...", text_align=ft.TextAlign.CENTER),
            padding=20
        )
        
        def load_dashboard_stats():
            try:
                headers = {"Authorization": f"Bearer {self.access_token}"}
                response = requests.get(f"{self.base_url}/dashboard/stats/", headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    stats_container.content = ft.Column([
                        ft.Text(f"Company: {self.user_data['company']['name']}", 
                               size=20, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                        ft.Divider(),
                        
                        # Stats Cards in a responsive grid
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Key Metrics", size=18, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                                ft.Container(height=10),
                                ft.Row([
                                    ft.Container(
                                        content=ft.Column([
                                            ft.Icon(ft.icons.PEOPLE, size=30, color=ft.colors.BLUE),
                                            ft.Text("Total Workers", size=12, text_align=ft.TextAlign.CENTER),
                                            ft.Text(str(data['total_workers']), 
                                                   size=24, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)
                                        ], alignment=ft.MainAxisAlignment.CENTER),
                                        padding=15,
                                        bgcolor=ft.colors.BLUE_50,
                                        border_radius=15,
                                        expand=True,
                                        margin=5
                                    ),
                                    ft.Container(
                                        content=ft.Column([
                                            ft.Icon(ft.icons.CHECK_CIRCLE, size=30, color=ft.colors.GREEN),
                                            ft.Text("Completed Today", size=12, text_align=ft.TextAlign.CENTER),
                                            ft.Text(str(data['completed_today']['count'] or 0), 
                                                   size=24, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)
                                        ], alignment=ft.MainAxisAlignment.CENTER),
                                        padding=15,
                                        bgcolor=ft.colors.GREEN_50,
                                        border_radius=15,
                                        expand=True,
                                        margin=5
                                    )
                                ]),
                                ft.Row([
                                    ft.Container(
                                        content=ft.Column([
                                            ft.Icon(ft.icons.PENDING, size=30, color=ft.colors.ORANGE),
                                            ft.Text("Pending Work", size=12, text_align=ft.TextAlign.CENTER),
                                            ft.Text(str(data['work_summary']['pending'] or 0), 
                                                   size=24, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)
                                        ], alignment=ft.MainAxisAlignment.CENTER),
                                        padding=15,
                                        bgcolor=ft.colors.ORANGE_50,
                                        border_radius=15,
                                        expand=True,
                                        margin=5
                                    ),
                                    ft.Container(
                                        content=ft.Column([
                                            ft.Icon(ft.icons.WARNING, size=30, color=ft.colors.RED),
                                            ft.Text("Low Stock Items", size=12, text_align=ft.TextAlign.CENTER),
                                            ft.Text(str(len(data['low_stock_materials'])), 
                                                   size=24, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)
                                        ], alignment=ft.MainAxisAlignment.CENTER),
                                        padding=15,
                                        bgcolor=ft.colors.RED_50,
                                        border_radius=15,
                                        expand=True,
                                        margin=5
                                    )
                                ])
                            ]),
                            padding=10
                        ),
                        
                        ft.Container(height=20),
                        
                        # Pending Work Section
                        ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Icon(ft.icons.WORK, size=24, color=ft.colors.BLUE),
                                    ft.Text("Pending Work by Worker", size=18, weight=ft.FontWeight.BOLD)
                                ], alignment=ft.MainAxisAlignment.START),
                                ft.Container(height=10),
                                ft.Container(
                                    content=ft.Column([
                                        ft.Text(f"• {item['worker__name']}: {item['pending_lots']} lots ({item['total_quantity']} pieces)")
                                        for item in data['pending_work_by_worker'][:8]
                                    ] if data['pending_work_by_worker'] else [ft.Text("No pending work", color=ft.colors.GREEN)]),
                                    padding=15,
                                    bgcolor=ft.colors.BLUE_50,
                                    border_radius=10
                                )
                            ]),
                            padding=10
                        ),
                        
                        ft.Container(height=20),
                        
                        # Low Stock Section
                        ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Icon(ft.icons.INVENTORY, size=24, color=ft.colors.RED),
                                    ft.Text("Low Stock Materials", size=18, weight=ft.FontWeight.BOLD)
                                ], alignment=ft.MainAxisAlignment.START),
                                ft.Container(height=10),
                                ft.Container(
                                    content=ft.Column([
                                        ft.Text(f"• {item['material__material_name']}: {item['current_quantity']} {item['material__unit']}", color=ft.colors.RED)
                                        for item in data['low_stock_materials'][:8]
                                    ] if data['low_stock_materials'] else [ft.Text("No low stock items", color=ft.colors.GREEN)]),
                                    padding=15,
                                    bgcolor=ft.colors.RED_50,
                                    border_radius=10
                                )
                            ]),
                            padding=10
                        )
                    ], scroll=ft.ScrollMode.AUTO)
                    page.update()
                else:
                    stats_container.content = ft.Text(f"Error loading dashboard: {response.status_code}")
                    page.update()
            except Exception as e:
                stats_container.content = ft.Text(f"Error loading dashboard: {str(e)}")
                page.update()
        
        # Load stats
        load_dashboard_stats()
        
        return ft.View(
            "/dashboard",
            [
                ft.AppBar(
                    title=ft.Text("Dashboard"),
                    bgcolor=ft.colors.BLUE,
                    actions=[
                        ft.IconButton(
                            ft.icons.LOGOUT,
                            on_click=lambda _: self.logout(page)
                        )
                    ]
                ),
                ft.Container(
                    content=ft.Column([
                        stats_container,
                        ft.Divider(),
                        ft.Text("Quick Actions", size=18, weight=ft.FontWeight.BOLD),
                        ft.Column([
                            ft.ElevatedButton(
                                "Add Worker", 
                                on_click=lambda _: self.show_add_worker_dialog(page),
                                bgcolor=ft.colors.BLUE,
                                color=ft.colors.WHITE,
                                width=300
                            ),
                            ft.ElevatedButton(
                                "Add Supplier", 
                                on_click=lambda _: self.show_add_supplier_dialog(page),
                                bgcolor=ft.colors.PURPLE,
                                color=ft.colors.WHITE,
                                width=300
                            ),
                            ft.ElevatedButton(
                                "Add Material", 
                                on_click=lambda _: self.show_add_material_dialog(page),
                                bgcolor=ft.colors.GREEN,
                                color=ft.colors.WHITE,
                                width=300
                            ),
                            ft.ElevatedButton(
                                "Distribute Work", 
                                on_click=lambda _: page.go("/work_distribution"),
                                bgcolor=ft.colors.RED,
                                color=ft.colors.WHITE,
                                width=300
                            ),
                            ft.ElevatedButton(
                                "Return Work", 
                                on_click=lambda _: page.go("/work_return"),
                                bgcolor=ft.colors.TEAL,
                                color=ft.colors.WHITE,
                                width=300
                            )
                        ])
                    ], scroll=ft.ScrollMode.AUTO)
                ),
                self.create_bottom_nav(page, 0)
            ]
        )
    
    def workers_view(self, page):
        if not self.access_token:
            page.go("/")
            return
        
        workers_list = ft.Column()
        
        def load_workers():
            try:
                headers = {"Authorization": f"Bearer {self.access_token}"}
                response = requests.get(f"{self.base_url}/workers/", headers=headers)
                
                if response.status_code == 200:
                    workers = response.json()['results']
                    workers_list.controls.clear()
                    
                    if not workers:
                        workers_list.controls.append(
                            ft.Text("No workers found", text_align=ft.TextAlign.CENTER)
                        )
                    else:
                        for worker in workers:
                            workers_list.controls.append(
                                ft.Container(
                                    content=ft.Column([
                                        ft.Text(worker['name'], size=16, weight=ft.FontWeight.BOLD),
                                        ft.Text(f"Skill: {worker['skill_type']}"),
                                        ft.Text(f"Mobile: {worker['mobile_number']}"),
                                        ft.Text(f"City: {worker['city']}")
                                    ]),
                                    padding=15,
                                    margin=5,
                                    bgcolor=ft.colors.BLUE_50,
                                    border_radius=10
                                )
                            )
                    page.update()
            except Exception as e:
                workers_list.controls = [ft.Text(f"Error: {str(e)}")]
                page.update()
        
        load_workers()
        
        return ft.View(
            "/workers",
            [
                ft.AppBar(
                    title=ft.Text("Workers"),
                    bgcolor=ft.colors.BLUE,
                    actions=[
                        ft.IconButton(
                            ft.icons.ADD,
                            on_click=lambda _: self.show_add_worker_dialog(page)
                        )
                    ]
                ),
                ft.Column([
                    ft.ElevatedButton(
                        "Refresh",
                        on_click=lambda _: load_workers(),
                        bgcolor=ft.colors.BLUE,
                        color=ft.colors.WHITE
                    ),
                    workers_list
                ], scroll=ft.ScrollMode.AUTO),
                self.create_bottom_nav(page, 1)
            ]
        )
    
    def suppliers_view(self, page):
        if not self.access_token:
            page.go("/")
            return
        
        suppliers_list = ft.Column()
        
        def load_suppliers():
            try:
                headers = {"Authorization": f"Bearer {self.access_token}"}
                response = requests.get(f"{self.base_url}/suppliers/", headers=headers)
                
                if response.status_code == 200:
                    suppliers = response.json()['results']
                    suppliers_list.controls.clear()
                    
                    if not suppliers:
                        suppliers_list.controls.append(
                            ft.Text("No suppliers found", text_align=ft.TextAlign.CENTER)
                        )
                    else:
                        for supplier in suppliers:
                            suppliers_list.controls.append(
                                ft.Container(
                                    content=ft.Column([
                                        ft.Text(supplier['name'], size=16, weight=ft.FontWeight.BOLD),
                                        ft.Text(f"Mobile: {supplier['mobile_number']}"),
                                        ft.Text(f"City: {supplier['city']}")
                                    ]),
                                    padding=15,
                                    margin=5,
                                    bgcolor=ft.colors.PURPLE_50,
                                    border_radius=10
                                )
                            )
                    page.update()
            except Exception as e:
                suppliers_list.controls = [ft.Text(f"Error: {str(e)}")]
                page.update()
        
        load_suppliers()
        
        return ft.View(
            "/suppliers",
            [
                ft.AppBar(
                    title=ft.Text("Suppliers"),
                    bgcolor=ft.colors.PURPLE,
                    actions=[
                        ft.IconButton(
                            ft.icons.ADD,
                            on_click=lambda _: self.show_add_supplier_dialog(page)
                        )
                    ]
                ),
                ft.Column([
                    ft.ElevatedButton(
                        "Refresh",
                        on_click=lambda _: load_suppliers(),
                        bgcolor=ft.colors.PURPLE,
                        color=ft.colors.WHITE
                    ),
                    suppliers_list
                ], scroll=ft.ScrollMode.AUTO),
                self.create_bottom_nav(page, 2)
            ]
        )
    
    def materials_view(self, page):
        if not self.access_token:
            page.go("/")
            return
        
        materials_list = ft.Column()
        
        def load_materials():
            try:
                headers = {"Authorization": f"Bearer {self.access_token}"}
                response = requests.get(f"{self.base_url}/materials/raw-materials/", headers=headers)
                
                if response.status_code == 200:
                    materials = response.json()['results']
                    materials_list.controls.clear()
                    
                    if not materials:
                        materials_list.controls.append(
                            ft.Text("No materials found", text_align=ft.TextAlign.CENTER)
                        )
                    else:
                        for material in materials:
                            materials_list.controls.append(
                                ft.Container(
                                    content=ft.Column([
                                        ft.Text(material['material_name'], size=16, weight=ft.FontWeight.BOLD),
                                        ft.Text(f"Unit: {material['unit']}"),
                                        ft.Text(f"Description: {material['description'] or 'N/A'}")
                                    ]),
                                    padding=15,
                                    margin=5,
                                    bgcolor=ft.colors.GREEN_50,
                                    border_radius=10
                                )
                            )
                    page.update()
            except Exception as e:
                materials_list.controls = [ft.Text(f"Error: {str(e)}")]
                page.update()
        
        load_materials()
        
        return ft.View(
            "/materials",
            [
                ft.AppBar(
                    title=ft.Text("Materials"),
                    bgcolor=ft.colors.GREEN,
                    actions=[
                        ft.IconButton(
                            ft.icons.ADD,
                            on_click=lambda _: self.show_add_material_dialog(page)
                        )
                    ]
                ),
                ft.Column([
                    ft.ElevatedButton(
                        "Refresh",
                        on_click=lambda _: load_materials(),
                        bgcolor=ft.colors.GREEN,
                        color=ft.colors.WHITE
                    ),
                    materials_list
                ], scroll=ft.ScrollMode.AUTO),
                self.create_bottom_nav(page, 3)
            ]
        )
    
    def stock_view(self, page):
        if not self.access_token:
            page.go("/")
            return
        
        stock_list = ft.Column()
        
        def load_stock():
            try:
                headers = {"Authorization": f"Bearer {self.access_token}"}
                response = requests.get(f"{self.base_url}/stock/current/", headers=headers)
                
                if response.status_code == 200:
                    stocks = response.json()['results']
                    stock_list.controls.clear()
                    
                    # Calculate summary
                    total_items = len(stocks)
                    low_stock_count = len([s for s in stocks if float(s['current_quantity']) < 10])
                    medium_stock_count = len([s for s in stocks if 10 <= float(s['current_quantity']) < 50])
                    good_stock_count = len([s for s in stocks if float(s['current_quantity']) >= 50])
                    
                    # Add summary cards
                    stock_list.controls.append(
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Stock Summary", size=18, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                                ft.Container(height=10),
                                ft.Column([
                                    ft.Row([
                                        ft.Container(
                                            content=ft.Column([
                                                ft.Icon(ft.icons.INVENTORY, size=24, color=ft.colors.BLUE),
                                                ft.Text("Total Items", size=12, text_align=ft.TextAlign.CENTER),
                                                ft.Text(str(total_items), size=20, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)
                                            ], alignment=ft.MainAxisAlignment.CENTER),
                                            padding=15,
                                            bgcolor=ft.colors.BLUE_50,
                                            border_radius=10,
                                            expand=True,
                                            margin=2
                                        ),
                                        ft.Container(
                                            content=ft.Column([
                                                ft.Icon(ft.icons.WARNING, size=24, color=ft.colors.RED),
                                                ft.Text("Low Stock", size=12, text_align=ft.TextAlign.CENTER),
                                                ft.Text(str(low_stock_count), size=20, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER, color=ft.colors.RED)
                                            ], alignment=ft.MainAxisAlignment.CENTER),
                                            padding=15,
                                            bgcolor=ft.colors.RED_50,
                                            border_radius=10,
                                            expand=True,
                                            margin=2
                                        )
                                    ]),
                                    ft.Row([
                                        ft.Container(
                                            content=ft.Column([
                                                ft.Icon(ft.icons.REMOVE_RED_EYE, size=24, color=ft.colors.ORANGE),
                                                ft.Text("Medium", size=12, text_align=ft.TextAlign.CENTER),
                                                ft.Text(str(medium_stock_count), size=20, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER, color=ft.colors.ORANGE)
                                            ], alignment=ft.MainAxisAlignment.CENTER),
                                            padding=15,
                                            bgcolor=ft.colors.ORANGE_50,
                                            border_radius=10,
                                            expand=True,
                                            margin=2
                                        ),
                                        ft.Container(
                                            content=ft.Column([
                                                ft.Icon(ft.icons.CHECK_CIRCLE, size=24, color=ft.colors.GREEN),
                                                ft.Text("Good", size=12, text_align=ft.TextAlign.CENTER),
                                                ft.Text(str(good_stock_count), size=20, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER, color=ft.colors.GREEN)
                                            ], alignment=ft.MainAxisAlignment.CENTER),
                                            padding=15,
                                            bgcolor=ft.colors.GREEN_50,
                                            border_radius=10,
                                            expand=True,
                                            margin=2
                                        )
                                    ])
                                ])
                            ]),
                            padding=10,
                            margin=5,
                            bgcolor=ft.colors.WHITE,
                            border_radius=15,
                            shadow=ft.BoxShadow(blur_radius=5, color=ft.colors.BLACK12)
                        )
                    )
                    
                    # Define low_stock_items
                    low_stock_items = [s for s in stocks if float(s['current_quantity']) < 10]
                    
                    # Add low stock alert if any
                    if low_stock_items:
                        stock_list.controls.append(
                            ft.Container(
                                content=ft.Column([
                                    ft.Row([
                                        ft.Icon(ft.icons.WARNING, size=20, color=ft.colors.RED),
                                        ft.Text("Low Stock Alert", size=16, weight=ft.FontWeight.BOLD, color=ft.colors.RED)
                                    ], alignment=ft.MainAxisAlignment.START),
                                    ft.Container(height=5),
                                    ft.Container(
                                        content=ft.Column([
                                            ft.Container(
                                                content=ft.Text(f"{item['material_name']}: {item['current_quantity']} {item['material_unit']}", 
                                                               color=ft.colors.RED, size=14),
                                                padding=8,
                                                margin=2,
                                                bgcolor=ft.colors.RED_100,
                                                border_radius=8
                                            )
                                            for item in low_stock_items[:5]  # Limit to 5 for mobile
                                        ]),
                                        padding=10,
                                        bgcolor=ft.colors.RED_50,
                                        border_radius=10
                                    )
                                ]),
                                padding=15,
                                margin=5,
                                bgcolor=ft.colors.WHITE,
                                border_radius=15,
                                shadow=ft.BoxShadow(blur_radius=5, color=ft.colors.BLACK12)
                            )
                        )
                    
                    # Add current stock items
                    if not stocks:
                        stock_list.controls.append(
                            ft.Text("No stock data found", text_align=ft.TextAlign.CENTER)
                        )
                    else:
                        for stock in stocks:
                            qty = float(stock['current_quantity'])
                            status_color = ft.colors.RED if qty < 10 else ft.colors.ORANGE if qty < 50 else ft.colors.GREEN
                            status_icon = ft.icons.WARNING if qty < 10 else ft.icons.REMOVE_RED_EYE if qty < 50 else ft.icons.CHECK_CIRCLE
                            
                            stock_list.controls.append(
                                ft.Container(
                                    content=ft.Row([
                                        ft.Container(
                                            content=ft.Icon(status_icon, size=24, color=status_color),
                                            width=40
                                        ),
                                        ft.Container(
                                            content=ft.Column([
                                                ft.Text(stock['material_name'], size=16, weight=ft.FontWeight.BOLD),
                                                ft.Text(f"Quantity: {stock['current_quantity']} {stock['material_unit']}", 
                                                       size=14, color=status_color),
                                                ft.Text(f"Updated: {stock['last_updated'][:10]}", size=12, color=ft.colors.GREY)
                                            ], alignment=ft.MainAxisAlignment.START, spacing=2),
                                            expand=True
                                        )
                                    ], alignment=ft.MainAxisAlignment.START),
                                    padding=15,
                                    margin=5,
                                    bgcolor=ft.colors.WHITE,
                                    border_radius=15,
                                    shadow=ft.BoxShadow(blur_radius=3, color=ft.colors.BLACK12)
                                )
                            )
                    page.update()
            except Exception as e:
                stock_list.controls = [ft.Text(f"Error: {str(e)}")]
                page.update()
        
        load_stock()
        
        return ft.View(
            "/stock",
            [
                ft.AppBar(
                    title=ft.Text("Stock"),
                    bgcolor=ft.colors.ORANGE
                ),
                ft.Column([
                    ft.ElevatedButton(
                        "Refresh",
                        on_click=lambda _: load_stock(),
                        bgcolor=ft.colors.ORANGE,
                        color=ft.colors.WHITE
                    ),
                    stock_list
                ], scroll=ft.ScrollMode.AUTO),
                self.create_bottom_nav(page, 4)
            ]
        )
    
    def work_distribution_view(self, page):
        if not self.access_token:
            page.go("/")
            return
        
        work_list = ft.Column()
        
        def load_work_distributions():
            try:
                headers = {"Authorization": f"Bearer {self.access_token}"}
                response = requests.get(f"{self.base_url}/work/distributions/", headers=headers)
                
                if response.status_code == 200:
                    works = response.json()['results']
                    work_list.controls.clear()
                    
                    if not works:
                        work_list.controls.append(
                            ft.Text("No work distributions found", text_align=ft.TextAlign.CENTER)
                        )
                    else:
                        for work in works:
                            work_list.controls.append(
                                ft.Container(
                                    content=ft.Column([
                                        ft.Text(f"Worker: {work['worker_name']}", size=16, weight=ft.FontWeight.BOLD),
                                        ft.Text(f"Work Type: {work['work_type_name']}"),
                                        ft.Text(f"Lot Size: {work['lot_size']}"),
                                        ft.Text(f"Status: {work['status']}"),
                                        ft.Text(f"Date: {work['distributed_date']}")
                                    ]),
                                    padding=15,
                                    margin=5,
                                    bgcolor=ft.colors.RED_50,
                                    border_radius=10
                                )
                            )
                    page.update()
            except Exception as e:
                work_list.controls = [ft.Text(f"Error: {str(e)}")]
                page.update()
        
        load_work_distributions()
        
        return ft.View(
            "/work_distribution",
            [
                ft.AppBar(
                    title=ft.Text("Work Distribution"),
                    bgcolor=ft.colors.RED,
                    actions=[
                        ft.IconButton(
                            ft.icons.ADD,
                            on_click=lambda _: self.show_add_work_distribution_dialog(page)
                        )
                    ]
                ),
                ft.Column([
                    ft.ElevatedButton(
                        "Refresh",
                        on_click=lambda _: load_work_distributions(),
                        bgcolor=ft.colors.RED,
                        color=ft.colors.WHITE
                    ),
                    work_list
                ], scroll=ft.ScrollMode.AUTO),
                self.create_bottom_nav(page, 5)
            ]
        )
    
    def work_return_view(self, page):
        if not self.access_token:
            page.go("/")
            return
        
        return_list = ft.Column()
        
        def load_work_returns():
            try:
                headers = {"Authorization": f"Bearer {self.access_token}"}
                response = requests.get(f"{self.base_url}/work/returns/", headers=headers)
                
                if response.status_code == 200:
                    returns = response.json()['results']
                    return_list.controls.clear()
                    
                    if not returns:
                        return_list.controls.append(
                            ft.Text("No work returns found", text_align=ft.TextAlign.CENTER)
                        )
                    else:
                        for ret in returns:
                            return_list.controls.append(
                                ft.Container(
                                    content=ft.Column([
                                        ft.Text(f"Distribution: {ret['distribution']['worker']['name']} - {ret['distribution']['work_type']['name']}", size=16, weight=ft.FontWeight.BOLD),
                                        ft.Text(f"Completed Quantity: {ret['completed_quantity']}"),
                                        ft.Text(f"Return Date: {ret['return_date']}")
                                    ]),
                                    padding=15,
                                    margin=5,
                                    bgcolor=ft.colors.TEAL_50,
                                    border_radius=10
                                )
                            )
                    page.update()
            except Exception as e:
                return_list.controls = [ft.Text(f"Error: {str(e)}")]
                page.update()
        
        load_work_returns()
        
        return ft.View(
            "/work_return",
            [
                ft.AppBar(
                    title=ft.Text("Work Return"),
                    bgcolor=ft.colors.TEAL
                ),
                ft.Column([
                    ft.ElevatedButton(
                        "Refresh",
                        on_click=lambda _: load_work_returns(),
                        bgcolor=ft.colors.TEAL,
                        color=ft.colors.WHITE
                    ),
                    return_list
                ], scroll=ft.ScrollMode.AUTO),
                self.create_bottom_nav(page, 5)  # Same as work distribution
            ]
        )
    
    def show_add_worker_dialog(self, page):
        """Show dialog to add new worker"""
        name_field = ft.TextField(label="Name", width=300)
        mobile_field = ft.TextField(label="Mobile Number", width=300)
        address_field = ft.TextField(label="Address", width=300, multiline=True)
        city_field = ft.TextField(label="City", width=300)
        skill_field = ft.Dropdown(
            label="Skill Type",
            width=300,
            options=[
                ft.dropdown.Option("stitching"),
                ft.dropdown.Option("button"),
                ft.dropdown.Option("collar"),
                ft.dropdown.Option("color")
            ]
        )
        machine_field = ft.TextField(label="Machine Type", width=300)
        language_field = ft.Dropdown(
            label="Language Preference",
            width=300,
            options=[
                ft.dropdown.Option("en", text="English"),
                ft.dropdown.Option("gu", text="Gujarati")
            ],
            value="en"
        )
        
        def save_worker(e):
            if not name_field.value or not mobile_field.value:
                page.snack_bar = ft.SnackBar(ft.Text("Name and mobile are required"))
                page.snack_bar.open = True
                page.update()
                return
            
            try:
                headers = {"Authorization": f"Bearer {self.access_token}"}
                data = {
                    "name": name_field.value,
                    "mobile_number": mobile_field.value,
                    "address": address_field.value or "",
                    "city": city_field.value or "",
                    "skill_type": skill_field.value or "stitching",
                    "machine_type": machine_field.value or "",
                    "language_preference": language_field.value or "en"
                }
                response = requests.post(f"{self.base_url}/workers/", json=data, headers=headers)
                
                if response.status_code == 201:
                    page.snack_bar = ft.SnackBar(ft.Text("Worker added successfully"))
                    page.snack_bar.open = True
                    dlg.open = False
                    page.go("/workers")  # Refresh the list
                else:
                    page.snack_bar = ft.SnackBar(ft.Text(f"Error: {response.text}"))
                    page.snack_bar.open = True
                page.update()
            except Exception as ex:
                page.snack_bar = ft.SnackBar(ft.Text(f"Error: {str(ex)}"))
                page.snack_bar.open = True
                page.update()
        
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Add New Worker"),
            content=ft.Container(
                content=ft.Column([
                    name_field,
                    mobile_field,
                    address_field,
                    city_field,
                    skill_field,
                    machine_field,
                    language_field
                ], tight=True, scroll=ft.ScrollMode.AUTO),
                width=350,
                height=500
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: setattr(dlg, 'open', False) or page.update()),
                ft.TextButton("Save", on_click=save_worker),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        page.dialog = dlg
        dlg.open = True
        page.update()
    
    def show_add_supplier_dialog(self, page):
        """Show dialog to add new supplier"""
        name_field = ft.TextField(label="Name", width=300)
        mobile_field = ft.TextField(label="Mobile Number", width=300)
        address_field = ft.TextField(label="Address", width=300)
        city_field = ft.TextField(label="City", width=300)
        
        def save_supplier(e):
            if not name_field.value or not mobile_field.value:
                page.snack_bar = ft.SnackBar(ft.Text("Name and mobile are required"))
                page.snack_bar.open = True
                page.update()
                return
            
            try:
                headers = {"Authorization": f"Bearer {self.access_token}"}
                data = {
                    "name": name_field.value,
                    "mobile_number": mobile_field.value,
                    "address": address_field.value or "",
                    "city": city_field.value or ""
                }
                response = requests.post(f"{self.base_url}/suppliers/", json=data, headers=headers)
                
                if response.status_code == 201:
                    page.snack_bar = ft.SnackBar(ft.Text("Supplier added successfully"))
                    page.snack_bar.open = True
                    dlg.open = False
                    page.go("/suppliers")
                else:
                    page.snack_bar = ft.SnackBar(ft.Text(f"Error: {response.text}"))
                    page.snack_bar.open = True
                page.update()
            except Exception as ex:
                page.snack_bar = ft.SnackBar(ft.Text(f"Error: {str(ex)}"))
                page.snack_bar.open = True
                page.update()
        
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Add New Supplier"),
            content=ft.Container(
                content=ft.Column([
                    name_field,
                    mobile_field,
                    address_field,
                    city_field
                ], tight=True),
                width=350,
                height=300
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: setattr(dlg, 'open', False) or page.update()),
                ft.TextButton("Save", on_click=save_supplier),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        page.dialog = dlg
        dlg.open = True
        page.update()
    
    def show_add_material_dialog(self, page):
        """Show dialog to add new material"""
        name_field = ft.TextField(label="Material Name", width=300)
        unit_field = ft.Dropdown(
            label="Unit",
            width=300,
            options=[
                ft.dropdown.Option("meter"),
                ft.dropdown.Option("roll"),
                ft.dropdown.Option("piece"),
                ft.dropdown.Option("kg")
            ]
        )
        desc_field = ft.TextField(label="Description", width=300, multiline=True)
        
        def save_material(e):
            if not name_field.value or not unit_field.value:
                page.snack_bar = ft.SnackBar(ft.Text("Name and unit are required"))
                page.snack_bar.open = True
                page.update()
                return
            
            try:
                headers = {"Authorization": f"Bearer {self.access_token}"}
                data = {
                    "material_name": name_field.value,
                    "unit": unit_field.value,
                    "description": desc_field.value or ""
                }
                response = requests.post(f"{self.base_url}/materials/raw-materials/", json=data, headers=headers)
                
                if response.status_code == 201:
                    page.snack_bar = ft.SnackBar(ft.Text("Material added successfully"))
                    page.snack_bar.open = True
                    dlg.open = False
                    page.go("/materials")
                else:
                    page.snack_bar = ft.SnackBar(ft.Text(f"Error: {response.text}"))
                    page.snack_bar.open = True
                page.update()
            except Exception as ex:
                page.snack_bar = ft.SnackBar(ft.Text(f"Error: {str(ex)}"))
                page.snack_bar.open = True
                page.update()
        
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Add New Material"),
            content=ft.Container(
                content=ft.Column([
                    name_field,
                    unit_field,
                    desc_field
                ], tight=True),
                width=350,
                height=250
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: setattr(dlg, 'open', False) or page.update()),
                ft.TextButton("Save", on_click=save_material),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        page.dialog = dlg
        dlg.open = True
        page.update()
    
    def show_add_work_distribution_dialog(self, page):
        """Show dialog to distribute work"""
        # Load workers and work types
        workers = []
        work_types = []
        materials = []
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            workers_response = requests.get(f"{self.base_url}/workers/", headers=headers)
            if workers_response.status_code == 200:
                workers = workers_response.json()['results']
            
            work_types_response = requests.get(f"{self.base_url}/work/work-types/", headers=headers)
            if work_types_response.status_code == 200:
                work_types = work_types_response.json()['results']
            
            materials_response = requests.get(f"{self.base_url}/materials/raw-materials/", headers=headers)
            if materials_response.status_code == 200:
                materials = materials_response.json()['results']
        except:
            pass
        
        worker_field = ft.Dropdown(
            label="Worker",
            width=300,
            options=[ft.dropdown.Option(str(w['id']), text=w['name']) for w in workers]
        )
        work_type_field = ft.Dropdown(
            label="Work Type",
            width=300,
            options=[ft.dropdown.Option(str(wt['id']), text=wt['name']) for wt in work_types]
        )
        lot_size_field = ft.TextField(label="Lot Size", width=300, keyboard_type=ft.KeyboardType.NUMBER)
        distributed_date_field = ft.TextField(label="Distributed Date", width=300, hint_text="YYYY-MM-DD")
        expected_return_date_field = ft.TextField(label="Expected Return Date", width=300, hint_text="YYYY-MM-DD")
        
        # Materials section
        materials_container = ft.Column()
        material_rows = []
        
        def add_material_row():
            material_field = ft.Dropdown(
                label="Material",
                width=200,
                options=[ft.dropdown.Option(str(m['id']), text=m['material_name']) for m in materials]
            )
            quantity_field = ft.TextField(label="Quantity", width=100, keyboard_type=ft.KeyboardType.NUMBER)
            remove_btn = ft.IconButton(ft.icons.REMOVE, on_click=lambda e: remove_material_row(material_row))
            
            material_row = ft.Row([material_field, quantity_field, remove_btn])
            material_rows.append({'material': material_field, 'quantity': quantity_field, 'row': material_row})
            materials_container.controls.append(material_row)
            page.update()
        
        def remove_material_row(row):
            for item in material_rows:
                if item['row'] == row:
                    material_rows.remove(item)
                    materials_container.controls.remove(row)
                    page.update()
                    break
        
        # Add initial material row
        add_material_row()
        
        def save_distribution(e):
            if not worker_field.value or not work_type_field.value or not lot_size_field.value:
                page.snack_bar = ft.SnackBar(ft.Text("Worker, work type, and lot size are required"))
                page.snack_bar.open = True
                page.update()
                return
            
            try:
                headers = {"Authorization": f"Bearer {self.access_token}"}
                
                # Prepare materials data
                materials_data = []
                for item in material_rows:
                    if item['material'].value and item['quantity'].value:
                        materials_data.append({
                            'material': int(item['material'].value),
                            'issued_quantity': float(item['quantity'].value)
                        })
                
                data = {
                    "worker": int(worker_field.value),
                    "work_type": int(work_type_field.value),
                    "lot_size": int(lot_size_field.value),
                    "distributed_date": distributed_date_field.value or str(date.today()),
                    "expected_return_date": expected_return_date_field.value or str(date.today()),
                    "materials": materials_data
                }
                
                response = requests.post(f"{self.base_url}/work/distributions/", json=data, headers=headers)
                
                if response.status_code == 201:
                    page.snack_bar = ft.SnackBar(ft.Text("Work distributed successfully"))
                    page.snack_bar.open = True
                    dlg.open = False
                    page.go("/work_distribution")
                else:
                    page.snack_bar = ft.SnackBar(ft.Text(f"Error: {response.text}"))
                    page.snack_bar.open = True
                page.update()
            except Exception as ex:
                page.snack_bar = ft.SnackBar(ft.Text(f"Error: {str(ex)}"))
                page.snack_bar.open = True
                page.update()
        
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Distribute Work"),
            content=ft.Container(
                content=ft.Column([
                    worker_field,
                    work_type_field,
                    lot_size_field,
                    distributed_date_field,
                    expected_return_date_field,
                    ft.Divider(),
                    ft.Text("Materials to Distribute", weight=ft.FontWeight.BOLD),
                    materials_container,
                    ft.ElevatedButton("Add Material", on_click=lambda e: add_material_row())
                ], tight=True, scroll=ft.ScrollMode.AUTO),
                width=400,
                height=600
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: setattr(dlg, 'open', False) or page.update()),
                ft.TextButton("Save", on_click=save_distribution),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        page.dialog = dlg
        dlg.open = True
        page.update()
    
    def logout(self, page):
        self.access_token = None
        self.user_data = None
        page.drawer = None
        page.go("/")


def main(page: ft.Page):
    app = GarmentApp()
    app.main(page)


if __name__ == "__main__":
    ft.app(target=main)