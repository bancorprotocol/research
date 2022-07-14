import { useState } from "react";

const useActiveClass = (default_class) =>{
    const [activClass, setActiveClass] = useState(default_class);
    const addActiveClass = (active_key)=>{
        setActiveClass(active_key);
    }

    return [activClass, addActiveClass];
}

export default useActiveClass;