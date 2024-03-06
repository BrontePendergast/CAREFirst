import React, { useState } from "react";
import Container from 'react-bootstrap/Container';

import './Messages.css'
import { Form, Row, Col, Button } from "react-bootstrap";

function Messages() {

    function makeid(length) {
        let result = '';
        const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
        const charactersLength = characters.length;
        let counter = 0;
        while (counter < length) {
          result += characters.charAt(Math.floor(Math.random() * charactersLength));
          counter += 1;
        }
        return result;
    }

    function returnMessage(event){
        if (event.keyCode === 13) {
            setScrollHeight(event);
        }
        else {
            console.log('resize');
            var textArea = document.getElementById("input-text");
            console.log(textArea);
            textArea.style.height = "auto !important";
            textArea.style.height = (textArea.scrollHeight) + "px !important";
            console.log(textArea.style.height);
        }
    };

    const [messages, setMessages] = useState([]);

    async function sendMessage(e) {

        var message = document.getElementById("input-text");
        console.log(message.value);
        if (message.value.length > 0) {
            var new_messages = [{'sender': 'you', 'message': message.value}, {'sender': 'bot', 'message': "Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum."}];
            setMessages([...messages, ...new_messages]);
            document.getElementById("input-text").value = "";
        }

    }

    const setScrollHeight = async (e) => {
        await sendMessage(e);
        document.getElementById("individual-messages-div").scrollTop = document.getElementById("individual-messages-div").scrollHeight;
        console.log(document.getElementById("individual-messages-div").scrollTop);
        console.log(document.getElementById("individual-messages-div").scrollHeight);
    }

    function thumbSelected(e) {
        console.log(e.target);
        var thumb = document.getElementById(e.target.id);
        var thumb_up = e.target.id.replace("thumbs-down", "thumbs-up");
        var thumb_down = e.target.id.replace("thumbs-up", "thumbs-down");

        var other_thumb = "";
        if (thumb.id===thumb_up){
            other_thumb = document.getElementById(thumb_down);
        }
        else {
            other_thumb = document.getElementById(thumb_up);
        }

        if (thumb.style.backgroundColor=='green'){
            thumb.style.backgroundColor = '#407481';
        }
        else if ((thumb.style.backgroundColor!='green') && (other_thumb.style.backgroundColor=='green')){
            other_thumb.style.backgroundColor = '#407481';
            thumb.style.backgroundColor = 'green';
        }
        else {
            thumb.style.backgroundColor = 'green';
        }
    }

    return (
        <Container fluid>
            <Container fluid id="individual-messages-div">
            {messages.map((message, i) => {
                if (message.sender=='bot'){
                    return (
                    <Row className={"individual-message-div"}>
                        <Col className={message.sender+" message-container mr-auto ml-0"} xs={"auto"}>
                        <Col></Col>
                            {message.message}
                            <div class="thumbs-container">
                                <Button className="thumbs-up btn" id={"thumbs-up-"+i} onClick={thumbSelected}>👍</Button>
                                <Button className="thumbs-down btn" id={"thumbs-down-"+i} onClick={thumbSelected}>👎</Button>
                            </div>
                        </Col>
                    </Row>)
                }
                else{
                    return (
                    <Row className={"individual-message-div"}>
                        <Col></Col>
                        <Col className={message.sender+" ml-auto"} xs={"auto"}>
                            {message.message}
                        </Col>
                    </Row>)
                }
                        
            })}
        </Container>
        <Row>
          <Col id="bottom-div">
          <Container fluid>
            <Row>
                <Col xs={11}>
                <Form.Control id="input-text" as="textarea" placeholder="Ask CareFirst AI your First Aid Questions!" onKeyUp={returnMessage}/>
                </Col>
                <Col xs={1} className="send_icon_div"><i class="fa-solid fa-circle-arrow-up send_icon fa-2xl send_icon" style={{color: "#74C0FC"}} onClick={setScrollHeight}></i></Col>
            </Row>
          </Container>
          </Col>
        </Row>
        </Container>
    );
  }
  

export default Messages;