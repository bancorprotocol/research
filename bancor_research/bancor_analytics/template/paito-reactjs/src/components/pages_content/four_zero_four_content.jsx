import React from 'react';
import { Link } from "react-router-dom";

export default function FourZeroFourContent() {
    return (
        <div>
            <div className="content-body">
                <div className="container-fluid">
                    <div className="row">
                        <div className="col-lg-10 mx-auto text-center pt-5">
                            <h2 className="page-title">Error 404</h2>
                        </div>
                    </div>
                </div>
                <div className="error-section">
                    <div className="container-fluid">
                        <div className="row">
                            <div className="col-lg-10 mx-auto">
                                <div className="error-msg-wrapper">
                                    <div className="error-msg">
                                        <h1>
                                            4 <span className="exc-icon">
                                                <i className="fa fa-exclamation-triangle" aria-hidden="true"></i>
                                            </span> 4
                                       </h1>
                                        <h2>Opps! Page is not found</h2>
                                        <p>Proin non tortor pharetra nisi ultricies rhoncus. Quisque posuere ut mi et viverra.
                                        Nunc
                                        lorem odio, aliquam vel ipsum vel, posuere posuere augue. Sed convallis dui ut erat
                                        consequat, in sodales sapien ornare.</p>
                                        <div className="back-button m-t-20">
                                            <Link to="/" className="btn btn-success"> Go to Dashboard </Link>
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
