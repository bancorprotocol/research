import React from 'react'
import { Formik, Field, ErrorMessage, Form } from 'formik';
import { Link } from "react-router-dom";

export default function LoginContent() {
    return (
        <div className="content-body">
            <div className="container">
                <div className="row">
                    <div className="col-lg-12 pt-5 text-center">
                        <h2 className="page-title mb-3">Login</h2>
                    </div>
                </div>
            </div>
            <div className="login-section">
                <div className="container">
                    <div className="row">
                        <div className="col-lg-5">
                            <div className="card-2 login-card">
                                <div className="card-body">
                                    <h2 className="card-title">Login Now</h2>
                                    <Formik
                                        initialValues={{ email: '', password: '' }}
                                        validate={values => {
                                            const errors = {};
                                            if (!values.email) {
                                                errors.email = 'Email Required';
                                            } else if (
                                                !/^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i.test(values.email)
                                            ) {
                                                errors.email = 'Invalid email address';
                                            }
                                            if(!values.password){
                                                errors.password = "Please Give The Password"
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
                                                        className="form-control mb-2"
                                                        placeholder="Email"
                                                    />
                                                    <ErrorMessage name="email" render={(msg) =>
                                                         <div className="invalid-form text-warning">{msg}</div>} />
                                                </div>

                                                <div className="form-group">
                                                    <Field
                                                        type="password"
                                                        name="password"
                                                        className="form-control mb-2"
                                                        placeholder="password"
                                                    />
                                                    <ErrorMessage name="password" render={(msg) =>
                                                        <div className="invalid-form text-warning">{msg}</div>} />
                                                </div>
                                                <div className="form-group">
                                                    <div className="custom-control custom-checkbox">
                                                        <Field
                                                            type="checkbox"
                                                            name="remember"
                                                            className="custom-control-input"
                                                            id="customCheck1"
                                                        />
                                                        <label className="custom-control-label" htmlFor="customCheck1">Remeber Me</label>
                                                         </div>
                                                        <label className="pull-right">
                                                            <Link to="/recover_password">
                                                                Recover Password?
                                                            </Link>
                                                        </label>
                                                    </div>
                                                <button type="submit"
                                                    disabled={isSubmitting}
                                                    className="custom-btn btn-block mb-4 submit"
                                                >
                                                    Login
                                                </button>
                                                <div className="row mb-4">
                                                    <div className="col-lg-6 mb-md-4">
                                                        <button type="button" className="custom-btn btn-block btn-facebook">Login with facebook</button>
                                                    </div>
                                                    <div className="col-lg-6">
                                                        <button type="button" className="custom-btn btn-block btn-twitter">Login with twitter</button>
                                                    </div>
                                                </div>
                                                <Link to="/register" className="register-btn">
                                                    Register Now <i className="fa fa-arrow-right"></i>
                                                </Link>
                                            </Form>
                                        )}
                                    </Formik>
                                </div>
                            </div>
                        </div>
                        <div className="col-lg-7">
                            <div className="promotion-section">
                                <h1 className="m-b-50">Buy and sell coins at the cryptopic without additional fees.</h1>
                                <p className="m-b-50">
                                    Proin non tortor pharetra nisi ultricies rhoncus. Quisque posuere ut mi et viverra. Nunc lorem odio, aliquam vel ipsum vel, posuere posuere augue. Sed convallis dui ut erat consequat, in sodales sapien ornare.</p>
                                <button className="custom-btn btn-success btn-radius">Go to Buy and Sell</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}
