import React from "react";
import { Col, Container, Row, Form } from "react-bootstrap";
import Header from "./components/Header";
import TopReasons from "./components/TopReasons";
import Messages from "./components/Messages";

import "./App.css"

function App() {
  const er_reasons = ["Chest Pains", "Shortness of Breath", "Fainting, Sudden Dizziness, or Weakness", "Sudden Blurring of Vision", "Changes in Mental Status, Confusion, or Disorientation"];
  const er_tooltip = [
    "Persistent chest pains may indicate that a heart attack is in progress and are a sure sign to get to the emergency room. There are other reasons a person may have chest pains (for example, indigestion), but it’s important to allow the medical personnel at the ER to make that evaluation. As a precaution, when going to the ER with chest pains, let someone else drive. Should you become worse or faint while driving, a serious accident may result.",
    "Shortness of breath can be caused by many things, some of which can be highly dangerous. Severe asthma attacks or serious allergic reactions can result in breathing difficulties. With some allergic reactions, swelling of the tongue may make any breathing extremely difficult, leading to a life-threatening condition. Anyone experiencing these sorts of conditions should go immediately to the ER.",
    "Many factors can result in a person fainting or feeling suddenly weak. Conditions such as cardiac arrhythmia, hypoglycemia, low blood pressure may contribute to restricting oxygen to the brain. Should a person faint without a known cause – such as donating blood – should be taken to the emergency room.",
    "Vision difficulties can indicate a stroke. Other causes include detached retina, blockage of arteries related to ocular nerves, and eye injuries. These and other conditions should be treated at once. Visit an emergency room immediately, however, do not attempt to drive.",
    "There are many causes for sudden disorientation. This type of confusion differs from Alzheimer’s, which comes on gradually over months or years. If a person suddenly becomes confused, has trouble talking, doesn’t recognize people they should know, or struggles to focus, then they should be taken to an emergency room for an evaluation. Several medical conditions can cause a sudden onset of severe changes in mental status. Included in these are strokes, seizures, medications, low insulin levels, and very high fevers. It’s never a good idea to self-diagnose, so a trip to the ER is warranted."
];

const uc_reasons = ["Upper Respiratory Infections and Viruses", "Sprains and Strains", "Sore Throats", "Urinary Tract Infections (UTI)", "Eye Infections or Issues"];
const uc_tooltip = [
  "One of the top reasons people visit urgent care is for help managing upper respiratory infections and viruses, such as colds, COVID, the flu, mononucleosis, or sinus infections. Since these conditions share similar symptoms, it can be challenging to know what’s causing you to feel sick.",
  "Suffering from a painful sprain or strain, such as a twisted ankle, sore wrist, or knee sprain, are all common reasons for visiting urgent care. Seeing a trained medical professional in these cases makes sense, as it’s difficult to tell on your own whether these injuries are fractures, sprains, or strains.",
  "Sore throats are rarely a medical emergency and often accompany viruses, but they can also signal a serious infection, such as strep throat. Strep throat is caused by a highly contagious bacteria, and if left untreated, it can worsen and cause serious complications.",
  "UTIs are common bacterial infections that affect women more often than men. Since UTIs don’t typically resolve on their own, and because they share symptoms with other gynecological problems, such as sexually transmitted diseases, it’s important to see a medical provider for an accurate diagnosis and treatment.",
  "If you’re struggling with an eye infection, such as pink eye, or you start experiencing other problematic eye issues, join the many people who visit urgent care for these reasons. Sometimes, eye infections are viral, but they can also be bacterial. Your medical provider advises you which you have, when to follow up with an eye doctor, and prescribes any necessary medication."
]

  return (
    <>
    <Header/>
    <Container className="mt-5 appcontainer">
      <Row>
        <Col md={3} className="topreasons">
          <TopReasons title="Top Reasons for ER" reason={er_reasons} icon_class="fa-li fa-solid fa-truck-medical fa_icon_amb fa-lg" tooltip={er_tooltip} placement="right"/>
        </Col>
        <Col md={6} className="pt-3 pl-5 pr-5 pb-0" id="messages-div">
          <Container fluid>
            <Row>
              <Messages/>
            </Row>
            </Container>
        </Col>
        <Col md={3} className="topreasons">
        <TopReasons title="Top Reasons for UC" reason={uc_reasons} icon_class="fa-li fa-solid fa-user-doctor fa_icon_doc fa-lg" tooltip={uc_tooltip} placement="left"/>
        </Col>
      </Row>
    </Container>
    </>
  );
}

export default App;
