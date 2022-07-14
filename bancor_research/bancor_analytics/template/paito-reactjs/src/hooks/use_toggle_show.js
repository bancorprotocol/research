import { useState } from "react";

const useToggleShow = ()=>{
    const [show,setShow] = useState(false);

    const showToggle = ()=>{
        setShow(!show);
    }
    return [show, showToggle];
}

export default useToggleShow;