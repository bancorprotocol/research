import React from 'react';
import PageLayout from "../../layouts/page_layout";
import CustomPagination from "../../components/custom/custom_pagination";

export default function Pagination() {
    return (
        <>
         <PageLayout>
            <CustomPagination/>
         </PageLayout>  
        </>
    )
}
