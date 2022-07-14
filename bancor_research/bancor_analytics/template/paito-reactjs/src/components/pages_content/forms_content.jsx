import React from 'react';
import { Editor } from 'react-draft-wysiwyg';
import 'react-draft-wysiwyg/dist/react-draft-wysiwyg.css';

export default function FormsContent() {
    
    return (
        <div className="content-body">
            <div className="container-fluid">
                <div className="row">
                    <div className="col-lg-12">
                        <h2 className="page-title">Forms</h2>
                    </div>
                </div>
            </div>
            <div className="forms-section">
                <div className="container-fluid">
                    <div className="row">
                        <div className="col-lg-12">
                            <div className="table-data">
                                <div className="card rounded-0">
                                    <div className="card-header">
                                        <h4 className="mb-0">
                                            Basic styles
                                        </h4>
                                    </div>
                                    <div id="basic-form" className="collapse show">
                                        <div className="card-body">
                                            <form>
                                                <div className="form-row">
                                                    <div className="col-lg-6 m-b-30">
                                                        <h6>Default Form</h6>
                                                        <input type="text" className="form-control" placeholder="First name" required />
                                                    </div>
                                                    <div className="col-lg-6 m-b-30">
                                                        <h6>Dropdown Form</h6>
                                                        <select className="custom-select">
                                                            <option value="1">Bitcoin</option>
                                                            <option value="2">Ethereum</option>
                                                            <option value="3">Repple</option>
                                                        </select>
                                                    </div>
                                                    <div className="col-lg-6 m-b-30">
                                                        <h6>File Browser</h6>
                                                        <div className="custom-file">
                                                            <input type="file" className="custom-file-input" id="customFile" required />
                                                            <label className="custom-file-label" htmlFor="customFile">Choose file</label>
                                                        </div>
                                                    </div>
                                                    <div className="col-lg-6 m-b-30">
                                                        <h6>Icon Form</h6>
                                                        <div className="input-group">
                                                            <div className="input-group-prepend">
                                                                <div className="input-group-text">
                                                                    <i className="icofont icofont-visa"></i>
                                                                </div>
                                                            </div>
                                                            <input type="text" className="form-control" placeholder="VISA" required />
                                                        </div>
                                                    </div>
                                                    <div className="col-lg-12 m-b-30">
                                                        <div className="form-group">
                                                            <h6>Message Form</h6>
                                                            <div className="textarea-wrapper border">
                                                                <Editor />
                                                            </div>
                                                        </div>
                                                        <div className="form-group">
                                                            <button className="btn btn-success button" type="submit">Submit</button>
                                                        </div>
                                                    </div>
                                                </div>
                                            </form>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

    )
}
