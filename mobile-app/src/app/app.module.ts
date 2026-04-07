import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule, HTTP_INTERCEPTORS } from '@angular/common/http';
import { ApiTimeoutInterceptor } from './interceptors/api-timeout.interceptor';
import { RouterModule, Routes } from '@angular/router';
import { IonicModule, IonicRouteStrategy } from '@ionic/angular';
import { RouteReuseStrategy } from '@angular/router';

import { AppComponent } from './app.component';
import { LoginPage } from './pages/login/login.page';
import { RegisterPage } from './pages/register/register.page';
import { DashboardPage } from './pages/dashboard/dashboard.page';
import { ModuleListPage } from './pages/module-list/module-list.page';
import { PrivacyPolicyPage } from './pages/privacy-policy/privacy-policy.page';
import { TermsOfServicePage } from './pages/terms-of-service/terms-of-service.page';
import { AboutPage } from './pages/about/about.page';

const routes: Routes = [
  { path: 'login', component: LoginPage },
  { path: 'register', component: RegisterPage },
  { path: 'dashboard', component: DashboardPage },
  { path: 'module/:key', component: ModuleListPage },
  { path: 'privacy-policy', component: PrivacyPolicyPage },
  { path: 'terms-of-service', component: TermsOfServicePage },
  { path: 'about', component: AboutPage },
  { path: 'page-one', redirectTo: 'dashboard', pathMatch: 'full' },
  { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
  { path: '**', redirectTo: 'login' }
];

@NgModule({
  declarations: [
    AppComponent
  ],
  imports: [
    BrowserModule,
    HttpClientModule,
    IonicModule.forRoot({
      animated: false
    }),
    RouterModule.forRoot(routes),
    LoginPage,
    RegisterPage,
    DashboardPage,
    ModuleListPage,
    PrivacyPolicyPage,
    TermsOfServicePage,
    AboutPage
  ],
  providers: [
    { provide: RouteReuseStrategy, useClass: IonicRouteStrategy },
    { provide: HTTP_INTERCEPTORS, useClass: ApiTimeoutInterceptor, multi: true },
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
