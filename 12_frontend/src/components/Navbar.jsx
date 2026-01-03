import Container from "react-bootstrap/Container";
import Nav from "react-bootstrap/Nav";
import Navbar from "react-bootstrap/Navbar";
import ThemeToggle from "./ThemeToggle";
import "../css/components/Navbar.css";

function Navbar1({ onHomeClick, onAboutClick }) {
  const handleHomeClick = (e) => {
    e.preventDefault();
    if (onHomeClick) {
      onHomeClick();
    }
  };

  const handleAboutClick = (e) => {
    e.preventDefault();
    if (onAboutClick) {
      onAboutClick();
    }
  };

  return (
    <Navbar expand="lg" className="glass-navbar" data-bs-theme="dark">
      <Container>
        <Navbar.Brand href="#home" onClick={handleHomeClick}>🔎</Navbar.Brand>
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav">
          <Nav className="w-100 align-items-center">
            <div className="navbar-links">
              <Nav.Link href="#home" onClick={handleHomeClick}>Home</Nav.Link>
              <Nav.Link href="#about" onClick={handleAboutClick}>About</Nav.Link>
            </div>
            <div className="navbar-theme-toggle">
              <ThemeToggle />
            </div>
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
}

export default Navbar1;