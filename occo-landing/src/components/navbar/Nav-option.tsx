"use client";
import { useState, useEffect } from "react";
import { usePathname } from "next/navigation";
import { ROUTES } from "../../routes/route";
import Link from "next/link";

export default function NavOption() {
  const params = usePathname();
  const [active, setActive] = useState(0);

  useEffect(() => {
    switch (params) {
      case "/":
        setActive(0);
        break;
      case "/about":
        setActive(1);
        break;
      case "/upgrade":
        setActive(2);
        break;
      case "/privacy":
        setActive(3);
        break;
      case "/rules":
        setActive(4);
        break;
    }
  }, [params]);

  return (
    <>
      <div
        className=" h-[90px] flex items-center px-2   border-0 max-[1300px]:w-fit"
        style={{
          color: active == 0 ? "white" : "",
          backgroundImage:
            active == 0
              ? `linear-gradient(180deg, rgba(27,10,28,0) 0%, rgba(170,74,186,0.2) 80%, rgba(213,104,209,0.4) 90%)`
              : "",
        }}
      >
        <Link href={ROUTES.PAGE.ROOT} className=" w-full  font-semibold	 text-[18px] max-[110px]:text-[12px]  max-[1300px]:text-[14px] text-center">
          Trang Chủ
        </Link>
      </div>

      <div
        className=" h-[90px] flex items-center px-2   border-0 max-[1300px]:w-fit"
        style={{
          color: active == 1 ? "white" : "",
          backgroundImage:
            active == 1
              ? "linear-gradient(180deg, rgba(27,10,28,0) 0%, rgba(170,74,186,0.2) 80%, rgba(213,104,209,0.4) 90%)"
              : "",
        }}
      >
        <Link href={ROUTES.PAGE.ABOUT} className=" w-full font-semibold text-[18px] max-[110px]:text-[12px]	 max-[1300px]:text-[14px] text-center">
          Về Occo
        </Link>
      </div>

      <div
        className=" h-[90px] flex items-center px-2   border-0 max-[1300px]:w-fit"
        style={{
          color: active == 3 ? "white" : "",
          backgroundImage:
            active == 3
              ? "linear-gradient(180deg, rgba(27,10,28,0) 0%, rgba(170,74,186,0.2) 80%, rgba(213,104,209,0.4) 90%)"
              : "",
        }}
      >
        <Link href={ROUTES.PAGE.PRIVACY} className=" w-full font-semibold	text-[18px] max-[110px]:text-[12px]  max-[1300px]:text-[14px] text-center  ">
          Chính sách bảo mật
        </Link>
      </div>

      <div
        className=" h-[90px] flex items-center px-2   border-0 max-[1300px]:w-fit"
        style={{
          color: active == 4 ? "white" : "",
          backgroundImage:
            active == 4
              ? "linear-gradient(180deg, rgba(27,10,28,0) 0%, rgba(170,74,186,0.2) 80%, rgba(213,104,209,0.4) 90%)"
              : "",
        }}
      >
        <Link href={ROUTES.PAGE.RULES} className=" w-full  font-semibold	text-[18px] max-[110px]:text-[12px]  max-[1300px]:text-[14px] text-center ">
          Thỏa thuận dịch vụ
        </Link>
      </div>

    

      <div className="h-[90px] flex items-center min-w-[154px]">
        <button className="bg-gradient-to-r from-p_1 to-p_2 text-white font-semibold rounded-full p-[1.5px]  " >
          <span className="flex w-full bg-navCor text-white rounded-full p-2 px-5"  style={{
         
         backgroundImage:
           active == 2
             ? "linear-gradient(to right bottom, #6603AC, #EF01BC )"
             : "",
            
       }}>
           <Link href={ROUTES.PAGE.UPGRADE} className="text-[16px] max-[110px]:text-[12px]  max-[1300px]:text-[14px] text-center">  Nâng cấp VIP</Link>
          </span>
        </button>
      </div>
    </>
  );
}
