import React, { useState } from "react";
import { Col, Container, Row, Form } from "react-bootstrap";
import { Image } from "react-bootstrap";

import "./About.css"


function About() {

  return (
    <Container>
    <Row>
        <Col ms={8} className="mt-5 mb-5 text-center">
            <h1 className="slogan-header">CareFirst AI</h1>
            <h2>Trusted First Aid Advisor in Your Pocket</h2>
        </Col>
    </Row>
    <Row className="info-section">
        <Col ms={6} className="bot-about">
            Powered by <a className = "info-link" href="https://www.langchain.com/" target="_blank">Langchain</a> and <a className = "info-link" href="https://openai.com/blog/gpt-3-5-turbo-fine-tuning-and-api-updates" target="_blank">GPT-3.5</a>, CareFirst is a singular solution that helps users begin to understand <b>what</b> their medical issue might be, <b>where</b> they should seek medical attention, and <b>how</b> it may be treated.
        </Col>
        <Col ms={6} className='im-logos'>
        <Image src="./assets/images/LangChain_logo.png" alt='Langchain' id="langchain-logo"/>
        <Image src="./assets/images/gpt-3_5.png" alt='GPT' id="gpt-35"/>
        </Col>
    </Row>

    <Row className="info-section">
    <Col ms={6} className='im-logos text-center'>
        <Image src="./assets/images/American_Red_Cross_logo.png" alt='Red Cross' id="red-cross"/>
    </Col>
        <Col ms={6} className="you-about">
            CareFirst is a <b>Retrieval Augmented Generation</b> app with health information backed by the  <a className = "info-link" href="https://www.redcross.ca/crc/documents/comprehensive_guide_for_firstaidcpr_en.pdf" target="_blank">American Red Cross Guidelines</a>: a trusted medical source that we parse through so you don't have to!
        </Col>
    </Row>

    <Row className="info-section">
        <Col ms={6} className="bot-about">
            Our goal is always the same: help you find the best possible solution to your first-aid needs. That's why we don't just rely on AI conversation. We encourage feedback from our users and our very own verified medical professionals. See transparent feedback on CareFirst AI on our <a className="info-link" href="/model" >Model page</a>.
        </Col>
        <Col ms={6} className='im-logos'>
        <Image src="./assets/images/feedback-image.png" alt='Feedback' id="feedback-image"/>
        </Col>
    </Row>
    
    <Row>
        <Col ms={12} className="text-center">
            <h1 className="slogan-header">Meet the Team</h1>
        </Col>
    </Row>

    <Row className="info-section">
    <Col ms={6} className="text-center">
        <Image src="./assets/images/profile_pic.jpg" alt='Charlie' id="charlie_pic" className="profile-pics"/>
    </Col>
    <Col ms={6} className="you-about text-center name-message">
        <h1 className="name-plate">Charlie Glass</h1>
        <br>
        </br>
        <p className="job-title">UX & Frontend Engineer</p>
    </Col>
    </Row>

    <Row className="info-section">
    <Col ms={6} className="bot-about text-center name-message">
        <h1 className="name-plate">Bronte Pendergast</h1>
        <br>
        </br>
        <p className="job-title">Data Scientist</p>
    </Col>
    <Col ms={6} className="text-center">
        <Image src="./assets/images/bronte.jpeg" alt='Bronte' id="bronte_pic" className="profile-pics"/>
    </Col>
    </Row>

    <Row className="info-section">
    <Col ms={6} className="text-center">
        <Image src="./assets/images/ambika.png" alt='Ambika' id="ambika_pic" className="profile-pics"/>
    </Col>
    <Col ms={6} className="you-about text-center name-message">
        <h1 className="name-plate">Ambika Gupta</h1>
        <br>
        </br>
        <p className="job-title">Research & Model Evaluation</p>
    </Col>
    </Row>

    <Row className="info-section">
    <Col ms={6} className="bot-about text-center name-message">
        <h1 className="name-plate">Ricardo Marin</h1>
        <br>
        </br>
        <p className="job-title">Backend Engineer</p>
    </Col>
    <Col ms={6} className="text-center">
        <Image src="./assets/images/ricardo.png" alt='Ricardo' id="ricardo_pic" className="profile-pics"/>
    </Col>
    </Row>

    <Row className="info-section">
    <Col ms={6} className="text-center">
        <Image src="./assets/images/jessica.png" alt='Jessica' id="jessica_pic" className="profile-pics"/>
    </Col>
    <Col ms={6} className="you-about text-center name-message">
        <h1 className="name-plate">Jessica Stockham</h1>
        <br>
        </br>
        <p className="job-title">Backend Engineer/Data Scientist</p>
    </Col>
    </Row>
    </Container>
  );
};    

export default About;
