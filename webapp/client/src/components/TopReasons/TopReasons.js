import React, { Component } from "react";
import Container from 'react-bootstrap/Container';

import './TopReasons.css'
import { OverlayTrigger, Popover, Row, Col } from "react-bootstrap";

function TopReasons({title, reason, icon_class, tooltip, placement}) {
    return (
    <Container fluid>
        <h6 class="bolder-header mb-4">{title}</h6>
        <ul class="fa-ul">
            {reason.map((r, i) => (
                <OverlayTrigger placement={placement} overlay={<Popover id="popover-basic">
                <Popover.Header as="h3">{r}</Popover.Header>
                <Popover.Body>
                {tooltip[i]}
                </Popover.Body>
                </Popover>}>
                <li class="reason-div"><i class={icon_class}></i>
                    {r}
                </li>
                </OverlayTrigger>
                        
            ))}
        </ul>
    </Container>
    );
  }
  

export default TopReasons;