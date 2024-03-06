import React from "react";
import Container from 'react-bootstrap/Container';
import Nav from 'react-bootstrap/Nav';
import Navbar from 'react-bootstrap/Navbar';

import './Header.css'
import { Image } from "react-bootstrap";

function Header() {
    return (
        <Navbar id="header-container">
        <Container>
          <Navbar.Brand href="/"><Image src="./assets/images/care_first_logo.jpg" alt='CareFirst Logo' id="logo"/></Navbar.Brand>
          <Nav className="me-auto" id="nav">
            <Nav.Link href="/" className="nav-link">Home</Nav.Link>
            <Nav.Link href="#about">About</Nav.Link>
            <Nav.Link href="#model">The Model</Nav.Link>
            <Nav.Link id="slogan">Call <b>911</b> for Emergency</Nav.Link>
          </Nav>
        </Container>
      </Navbar>
    );
  }
  

export default Header;