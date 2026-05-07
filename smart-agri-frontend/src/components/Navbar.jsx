import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import LanguageSwitcher from "./LanguageSwitcher";
import "./Navbar.css";

function Navbar() {
  const { t } = useTranslation();

  return (
    <nav className="navbar">
      <h2 className="logo">{t("appName")}</h2>

      <div className="nav-links">
        <Link to="/dashboard">{t("dashboard")}</Link>
        <Link to="/crop">{t("cropDetection")}</Link>
        <Link to="/livestock">{t("livestockHealth")}</Link>
        <Link to="/marketplace">{t("marketplace")}</Link>
        <Link to="/schemes">{t("schemes")}</Link>

        {/* Language dropdown */}
        <LanguageSwitcher />
      </div>
    </nav>
  );
}

export default Navbar;
