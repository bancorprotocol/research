import React from 'react'
import { Formik, Field, ErrorMessage, Form } from 'formik';
import { Link } from "react-router-dom";
export default function RecoverPasswordContent() {
    return (
        <div className="content-body">
            <div className="container">
                <div className="row">
                    <div className="col-lg-12 text-center py-4">
                        <h2 className="page-title">Recover Password</h2>
                    </div>
                </div>
            </div>
            <div className="login-section mb-5">
                <div className="container">
                    <div className="row">
                        <div className="col-lg-5">
                            <div className="card-2 login-card register-card">
                                <div className="card-body">
                                    <h2 className="card-title">Recover Now</h2>
                                    <Formik
                                        initialValues={{ email: '' }}
                                        validate={values => {
                                            const errors = {};
                                            if (!values.email) {
                                                errors.email = 'Email Required';
                                            } else if (
                                                !/^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i.test(values.email)
                                            ) {
                                                errors.email = 'Invalid email address';
                                            }
                                            return errors;
                                        }}
                                        onSubmit={(values, { setSubmitting }) => {
                                            setTimeout(() => {
                                                console.log(JSON.stringify(values, null, 2));
                                                setSubmitting(false);
                                            }, 400);
                                        }}
                                    >
                                        {({ isSubmitting }) => (
                                            <Form>
                                                <div className="form-group">
                                                    <Field
                                                        type="email"
                                                        name="email"
                                                        className="form-control"
                                                        placeholder="Email"
                                                    />
                                                    <ErrorMessage name="email" render={(msg) => <div className="invalid-form text-warning">{msg}</div>} />
                                                </div>
                                                <button type="submit"
                                                    disabled={isSubmitting}
                                                    className="custom-btn-2 btn-block mb-4"
                                                >
                                                    Recover Now
                                                </button>
                                                <Link to="/login" className="register-btn">
                                                    GO TO LOGIN PAGE <i className="fa fa-arrow-right"></i>
                                                </Link>
                                            </Form>
                                        )}
                                    </Formik>
                                </div>
                            </div>
                        </div>
                        <div className="col-lg-7">
                            <div className="promotion-section">
                                <h1 className="m-b-40">Buy and sell coins at the cryptopic without additional fees.</h1>
                                <p className="m-b-40">Proin non tortor pharetra nisi ultricies rhoncus. Quisque posuere ut mi et viverra. Nunc lorem
                                odio, aliquam vel ipsum vel, posuere posuere augue. Sed convallis dui ut erat consequat,
                                    in sodales sapien ornare.</p>
                                <button className="custom-btn btn-success-2 btn-radius">Go to Buy and Sell</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}
