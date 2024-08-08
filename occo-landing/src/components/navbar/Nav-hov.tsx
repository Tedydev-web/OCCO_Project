"use client";
import { useEffect, useState, useMemo } from "react";
import { usePathname } from "next/navigation";

import Link from "next/link";
import { ROUTES } from "@/routes/route";
import Image from "next/image";
import logo from "@@/asset/images/avt1.png";
import { Turret_Road } from "next/font/google";
const turrant=Turret_Road({

  weight: '500',
  subsets:['latin'],

})
export default function NavHov() {
  const params = usePathname();
  const [currentPage, setCurrentPage] = useState(0);
  const [openSlide, setOpenSlide] = useState(0);
  const [active, setActive] = useState(0);

  const handleOver = (event: any) => {
    event.stopPropagation();
    setOpenSlide(0);
  };

  const handleChoose = (event: any) => {
    event.stopPropagation();
    setOpenSlide(0);
    setCurrentPage(1);
  };
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

  useEffect(() => {
    setOpenSlide(0);
  }, [currentPage, openSlide]);

  return (
    <>
      <div>
        <div className="drawer " onClick={() => setOpenSlide(1)}>
          <input
            id="my-drawer"
            type="checkbox"
            className="drawer-toggle"
            checked={openSlide == 0 ? false : true}
            readOnly
          />
          <div className="drawer-content  flex justify-end">
            <label
              htmlFor="my-drawer"
              className="btn btn-primary drawer-button bg-navCor border-0  px-0"
            >
              <svg
                className="h-[35px] w-[35px]  "
                fill="none"
                viewBox="0 0 24 24"
                stroke="white"
                aria-hidden="true"
              >
                <path d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
              </svg>
            </label>
          </div>
          <div className="drawer-side ">
            <label
              htmlFor="my-drawer"
              aria-label="close sidebar"
              className="drawer-overlay"
              onClick={(event) => handleOver(event)}
            ></label>
            <ul className="menu p-4 w-80 min-h-full  bg-navCor text-white  ">
              <div className="flex flex-row gap-3">
                <span className="-m-1.5 p-1.5">
                  <Link href="/">
                    <Image
                      src={logo}
                      alt="Tok"
                      width={40}
                      height={40}
                      className="rounded-full"
                      quality={100}
                    />
                  </Link>
                </span>
                <span className="flex items-center h-[49px] w-[50px] text-xl bg-gradient-to-r from-pink-500 to-purple-500 text-transparent bg-clip-text font-bold">
                  <Link href="/" className={`${turrant.className} text-[32px] max-lg:text-[20px]`}>Occo</Link>
                </span>
              </div>

              <li
                className="pt-3 active:text-red"
                onClick={(event) => handleChoose(event)}
              >
                <Link
                  href={ROUTES.PAGE.ROOT}
                  style={{ color: active == 0 ? "#A11BC7" : "white" }}
                  className="font-bold"
                >
                  Trang Chủ
                </Link>
              </li>
              <li className="pt-3" onClick={(event) => handleChoose(event)}>
                <Link
                  href={ROUTES.PAGE.ABOUT}
                  style={{ color: active == 1 ? "#A11BC7" : "white" }}
                  className="font-bold"
                >
                  Về Occo
                </Link>
              </li>
              <li className="pt-3" onClick={(event) => handleChoose(event)}>
                <Link
                  href={ROUTES.PAGE.UPGRADE}
                  style={{ color: active == 2 ? "#A11BC7" : "white" }}
                  className="font-bold"
                >
                  Nâng cấp vip
                </Link>
              </li>
              <li className="pt-3" onClick={(event) => handleChoose(event)}>
                <Link
                  href={ROUTES.PAGE.PRIVACY}
                  style={{ color: active == 3 ? "#A11BC7" : "white" }}
                  className="font-bold"
                >
                  Chính sách bảo mật
                </Link>
              </li>

              <li className="pt-3" onClick={(event) => handleChoose(event)}>
                <Link
                  href={ROUTES.PAGE.RULES}
                  style={{ color: active == 4 ? "#A11BC7" : "white" }}
                  className="font-bold"
                >
                  Thỏa thuận dịch vụ
                </Link>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </>
  );
}
