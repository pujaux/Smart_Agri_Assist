import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import LanguageSwitcher from "../components/LanguageSwitcher";
import "./Login.css";

function Login() {
  const navigate = useNavigate();
  const { t } = useTranslation();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleLogin = (e) => {
    e.preventDefault();
    navigate("/dashboard");
  };

  return (
    <div className="login-fullscreen">
      
      {/* Language dropdown */}
      <div className="language-box">
        <LanguageSwitcher />
      </div>

      <div className="login-overlay">
        <div className="login-card">
          <h2>{t("appName")}</h2>
          <p>{t("farmerLogin")}</p>

          <form onSubmit={handleLogin}>
            <div className="input-group">
              <label>{t("email")}</label>
              <input
                type="email"
                placeholder={t("email")}
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>

            <div className="input-group">
              <label>{t("password")}</label>
              <input
                type="password"
                placeholder={t("password")}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>

            <button type="submit" className="login-btn">
              {t("login")}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default Login;
