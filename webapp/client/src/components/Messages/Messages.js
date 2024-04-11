import React, { useState, useEffect } from "react";
import Container from 'react-bootstrap/Container';

import './Messages.css'
import { OverlayTrigger, Popover, Form, Row, Col, Button } from "react-bootstrap";

import API from '../../utils/API';

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

    const [messages, setMessages] = useState([{'sender': 'bot', 'message': 'If this is a medical emergency, please dial 911 immediately or go to the nearest emergency room.', 'page': 'N/A', 'message_id': makeid(6)}]);
    const [isTyping, setIsTyping] = useState(false);
    const [conversation_id, setConversationID] = useState(makeid(6));
    const [showTooltip, setShowTooltip] = useState({"message-0": false});

    const setShowTooltipTrue = function(event){
        // alert(event.target.id.substr(event.target.id.length-1));
        const targ = event.target.id.replace("popover-basic ", "").replace("thumbs-up-"+event.target.id.substr(event.target.id.length-1)+" ", "").replace("thumbs-down-"+event.target.id.substr(event.target.id.length-1)+" ", "");
        console.log(event.target);
        console.log(targ);
        console.log(showTooltip);
        if (showTooltip.hasOwnProperty(targ)){
            console.log("it's there");
            const new_obj = showTooltip;
            new_obj[targ] = true;
            setShowTooltip({...showTooltip, ...new_obj});
            console.log(showTooltip);
        }
        else{
            var added = {};
            added[targ] = true;
            setShowTooltip({...showTooltip, ...added})
        };
    };

    const setShowTooltipFalse = function(event){
        const targ = event.target.id.replace("popover-basic ", "").replace("thumbs-up-"+event.target.id.substr(event.target.id.length-1)+" ", "").replace("thumbs-down-"+event.target.id.substr(event.target.id.length-1)+" ", "");
        console.log(targ);
        console.log(showTooltip);
        if (showTooltip.hasOwnProperty(targ)){
            console.log("it's there");
            const new_obj = showTooltip;
            new_obj[targ] = false;
            setShowTooltip({...showTooltip, ...new_obj});
            console.log(showTooltip);
        }
        else{
            var added = {};
            added[targ] = false;
            setShowTooltip({...showTooltip, ...added})
        };
    };

    useEffect(() => {
        console.log('Updated messages:', messages);
      }, [messages]); // Add messages as a dependency to the useEffect

    async function sendMessage(e) {

        const messageSetter = () => {
            return new Promise((resolve) => {
                console.log('messages 1');
                console.log(messages);
                setMessages((prevMessages) => [...prevMessages, ...new_messages]);
                console.log('messages should be set now');
                console.log(messages);
                resolve("success");
            });
        };

        var message = document.getElementById("input-text").value;
        console.log("message value");
        console.log(message);
        if (message.length > 0) {
            // var output = await API.sendQuery(message.value);
            var new_messages = [{'sender': 'you', 'message': message, 'page': 'N/A'}];
            console.log(new_messages);
            // var new_messages = [{'sender': 'you', 'message': message.value}, {'sender': 'bot', 'message': output}];
            const set_message =  messageSetter();
            document.getElementById("input-text").value = "";
            console.log("sendMessage");
            console.log(messages);
            receiveMessage(message);        
        }

    }

    async function receiveMessage(message) {
        setIsTyping(true);
        document.getElementById("individual-messages-div").scrollTop = document.getElementById("individual-messages-div").scrollHeight;
        console.log(document.getElementById("individual-messages-div").scrollTop);
        console.log(document.getElementById("individual-messages-div").scrollHeight);
        var output = await API.sendQuery(message, conversation_id);
        var answer = output["answer"];
        var page = output["page"];
        var message_id = output["message_id"];
        setIsTyping(false);
        // document.getElementById("typingCheck").style.visiblity = "hidden";
        var new_messages_received = [{'sender': 'bot', 'message': answer, 'page': page, 'message_id': message_id}];
        console.log("messages");
        console.log(messages);
        await setMessages((prevMessages) => [...prevMessages, ...new_messages_received]);
        document.getElementById("individual-messages-div").scrollTop = document.getElementById("individual-messages-div").scrollHeight;
        console.log(document.getElementById("individual-messages-div").scrollTop);
        console.log(document.getElementById("individual-messages-div").scrollHeight);
        console.log(messages);

    }

    const setScrollHeight = async (e) => {
        await sendMessage(e);
        document.getElementById("individual-messages-div").scrollTop = document.getElementById("individual-messages-div").scrollHeight;
        console.log(document.getElementById("individual-messages-div").scrollTop);
        console.log(document.getElementById("individual-messages-div").scrollHeight);
    }

    function thumbSelected(e) {
        console.log(e.target);
        console.log("message id: "+e.target.dataset.messageid);
        var thumb = document.getElementById(e.target.id);
        var messageId = e.target.dataset.messageid;
        var thumb_up = e.target.id.replace("thumbs-down", "thumbs-up");
        var thumb_down = e.target.id.replace("thumbs-up", "thumbs-down");
        var feedback_obj = {};

        var other_thumb = "";
        if (thumb.id===thumb_up){
            other_thumb = document.getElementById(thumb_down);
        }
        else {
            other_thumb = document.getElementById(thumb_up);
        }

        if (thumb.style.backgroundColor=='green'){
            thumb.style.backgroundColor = '#407481';
            // feedback_obj['feedback'] = "";
        }
        else if ((thumb.style.backgroundColor!='green') && (other_thumb.style.backgroundColor=='green')){
            other_thumb.style.backgroundColor = '#407481';
            thumb.style.backgroundColor = 'green';

            if (e.target.id.includes('thumbs-up')) {
                feedback_obj['feedback'] = "True";
            }
            else {
                feedback_obj['feedback'] = "False";
            }
            API.sendFeedback(feedback_obj, messageId);
        }
        else {
            thumb.style.backgroundColor = 'green';

            if (e.target.id.includes('thumbs-up')) {
                feedback_obj['feedback'] = "True";
            }
            else {
                feedback_obj['feedback'] = "False";
            }
            API.sendFeedback(feedback_obj, messageId);
        }
        // API.sendFeedback(feedback_obj, messageId);
    }

    // document.getElementById("page-tooltip").onmouseover = function(){
    //     setShowTooltip(true);
    // };

    // document.getElementById("page-tooltip").onmouseleave = function(){
    //     setShowTooltip(false);
    // };

    // document.getElementsByClassName("bot").onmouseover = function(){
    //     setShowTooltip(true);
    // };

    // document.getElementsByClassName("bot").onmouseleave = function(){
    //     setShowTooltip(false);
    // };

    return (
        <>
        <Container fluid>
            <Container fluid id="individual-messages-div">
            {messages.map((message, i) => {
                if ((message.sender=='bot') && (i==0)){
                    return (
                    <Row className={"individual-message-div"} id={"message-"+i}>
                        <Col className={message.sender+" message-container mr-auto ml-0"} id={"message-"+i} onMouseEnter={setShowTooltipTrue} onMouseLeave={setShowTooltipFalse} xs={"auto"}>
                            {message.message}
                        </Col>
                    </Row>
                    )
                }
                else if (message.sender=='bot'){
                    return (
                        <OverlayTrigger placement='top' show={showTooltip['message-'+i] || showTooltip['pop-'+i]}  overlay={<Popover onMouseEnter={setShowTooltipTrue} onMouseLeave={setShowTooltipFalse} id={"popover-basic pop-"+i}>
                        <Popover.Header as="h3" id={"pop-"+i}><a href="https://www.redcross.ca/crc/documents/comprehensive_guide_for_firstaidcpr_en.pdf" target="_blank">Red Cross Guidelines</a></Popover.Header>
                        <Popover.Body id={"pop-"+i}>
                        {message.page}
                        </Popover.Body>
                        </Popover>}>
                        <Row className={"individual-message-div"} id={"message-"+i}>
                            <Col className={message.sender+" message-container mr-auto ml-0"} id={"message-"+i} onMouseEnter={setShowTooltipTrue} onMouseLeave={setShowTooltipFalse} xs={"auto"}>
                                {message.message}
                                <div class="thumbs-container">
                                    <Button className="thumbs-up btn" data-messageid={message.message_id} id={"thumbs-up-"+i+" message-"+i} onClick={thumbSelected} onMouseLeave={setShowTooltipFalse}>👍</Button>
                                    <Button className="thumbs-down btn" data-messageid={message.message_id} id={"thumbs-down-"+i+" message-"+i} onClick={thumbSelected} onMouseLeave={setShowTooltipFalse}>👎</Button>
                                </div>
                            </Col>
                        </Row>
                        </OverlayTrigger>
                        )
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
            {isTyping &&
                    <Row className={"individual-message-div"} id="typingCheck">
                        <Col className={"bot message-container mr-auto ml-0"} xs={"auto"}>
                        <div class="ticontainer">
                            <div class="tiblock">
                            <div class="tidot"></div>
                            <div class="tidot"></div>
                            <div class="tidot"></div>
                            </div>
                        </div>
                        </Col>
                    </Row>
        }
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
      </>
    );
  }
  

export default Messages;