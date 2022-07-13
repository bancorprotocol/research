import React from 'react';
import { Col, Container, Row } from 'reactstrap';
import Navigation from '../navigation/Navigation';
import Structure from './components/Structure';
import ScssStructure from './components/ScssStructure';
import NavigationBottom from '../navigation/NavigationBottom';

const FileStructure = () => (
  <Container className="documentation">
    <Row>
      <Col md={12}>
        <h3 className="page-title">Documentation / File Structure</h3>
      </Col>
    </Row>
    <Row className="documentation__main">
      <Col md={12} lg={3} xl={3} sm={12} xs={12} className="documentation__nav">
        <Navigation active="file_structure" />
      </Col>
      <Col md={12} lg={9} xl={9} sm={12} xs={12}>
        <Structure />
        <ScssStructure />
      </Col>
    </Row>
    <NavigationBottom
      prevLink="/documentation/installation"
      prevTitle="Installation"
      nextLink="/documentation/components"
      nextTitle="Components"
    />
  </Container>
);

export default FileStructure;
