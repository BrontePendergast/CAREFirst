import React from "react";
import { Col, Container, Row } from "react-bootstrap";
import { Image } from "react-bootstrap";
import { OverlayTrigger, Popover } from "react-bootstrap";


import "./Model.css"


function Model() {

  return (
    <Container>
    <Row className="divider-row text-center">
        <Col ms={6} className="placeholder-col">
                <Row>
                    <Col ms={12} className="mb-5">
                        <h1>Successes</h1>
                    </Col>
                </Row>
                <OverlayTrigger placement="top" overlay={<Popover id="popover-basic">
                <Popover.Header as="h3">Chest Pains</Popover.Header>
                <Popover.Body>
                Our verified experts agree with CareFirst AI on chest pains: if it's persistent, it could be a serious medical issue that requires immediate attention.
                </Popover.Body>
                </Popover>}>
                <Row className="tile-row">
                    <Col ms={12} className="mt-3 mb-3 bot-model">
                        Chest Pains
                        <div className="verified-container-model">
                        <Image  src="./assets/images/feedback-image.png" alt='Feedback' id="feedback-image-model"/>
                        99%
                    </div>
                    </Col>
                </Row>
                </OverlayTrigger>

                <OverlayTrigger placement="top" overlay={<Popover id="popover-basic">
                <Popover.Header as="h3">Sprains & Strains</Popover.Header>
                <Popover.Body>
                Medical professionals like the follow-up questions CareFirst AI asks the user. They agree that most require an Urgent Care visit at the most, and rarely an Emergency Department visit.
                </Popover.Body>
                </Popover>}>
                <Row className="tile-row">
                    <Col ms={12} className="mt-3 mb-3 bot-model">
                        Sprains & Strains
                        <div className="verified-container-model">
                        <Image  src="./assets/images/feedback-image.png" alt='Feedback' id="feedback-image-model"/>
                        98%
                    </div>
                    </Col>
                </Row>
                </OverlayTrigger>

                <OverlayTrigger placement="top" overlay={<Popover id="popover-basic">
                <Popover.Header as="h3">Shortness of Breath</Popover.Header>
                <Popover.Body>
                Shortness of breath can be caused by many underlying medical problems, and our experts find that CareFirst AI navigate the user's queries to give sound advice the vast majority of the time.
                </Popover.Body>
                </Popover>}>
                <Row className="tile-row">
                    <Col ms={12} className="mt-3 mb-3 bot-model">
                        Shortness of Breath
                        <div className="verified-container-model">
                        <Image  src="./assets/images/feedback-image.png" alt='Feedback' id="feedback-image-model"/>
                        98%
                    </div>
                    </Col>
                </Row>
                </OverlayTrigger>
        </Col>
        <Col ms={6} className="text-center divider-col">
        <Row>
                    <Col ms={12} className="mb-5">
                        <h1>Struggles</h1>
                    </Col>
                </Row>
                <OverlayTrigger placement="top" overlay={<Popover id="popover-basic">
                <Popover.Header as="h3">Small Cuts</Popover.Header>
                <Popover.Body>
                    Medical experts see errors in CareFirst AI's ability to analyze the severity of a cut. Their advice: if the cut looks deeper than surface level, seek medical attention.
                </Popover.Body>
                </Popover>}>
                <Row className="tile-row">
                    <Col ms={12} className="mt-3 mb-3 you-model">
                        Small Cuts
                        <div className="verified-container-model">
                        <Image  src="./assets/images/feedback-image.png" alt='Feedback' id="feedback-image-model"/>
                        72%
                    </div>
                    </Col>
                </Row>
                </OverlayTrigger>

                <OverlayTrigger placement="top" overlay={<Popover id="popover-basic">
                <Popover.Header as="h3">COVID</Popover.Header>
                <Popover.Body>
                    CareFirst AI has difficulty differentiating between COVID and the flu. For the safety of you and others, if you are experiencing flu-like symptoms, take a COVID test to see if social isolation is necessary.
                </Popover.Body>
                </Popover>}>
                <Row className="tile-row">
                    <Col ms={12} className="mt-3 mb-3 you-model">
                        COVID
                        <div className="verified-container-model">
                        <Image  src="./assets/images/feedback-image.png" alt='Feedback' id="feedback-image-model"/>
                        74%
                    </div>
                    </Col>
                </Row>
                </OverlayTrigger>

                <OverlayTrigger placement="top" overlay={<Popover id="popover-basic">
                <Popover.Header as="h3">Sudden Blurring of Vision</Popover.Header>
                <Popover.Body>
                    CareFirst AI has trouble providing much advice beyond seeking medical attention for blurry vision. Often that is the solution, but medical experts prefer to see CareFirst AI offer more guidance.
                </Popover.Body>
                </Popover>}>
                <Row className="tile-row">
                    <Col ms={12} className="mt-3 mb-3 you-model">
                        Sudden Blurring of Vision
                        <div className="verified-container-model">
                        <Image  src="./assets/images/feedback-image.png" alt='Feedback' id="feedback-image-model"/>
                        81%
                    </div>
                    </Col>
                </Row>
                </OverlayTrigger>
        </Col>
    </Row>
    </Container>
  );
};    

export default Model;
