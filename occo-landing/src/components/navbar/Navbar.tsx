"use client";
import Image from "next/image";
import logo from "../../../public/asset/images/avt1.png"
import Link from "next/link";
import star from "../../../public/asset/images/star.png";
import NavOption from "./Nav-option";
import { ROUTES } from "@/routes/route";
import NavHov from "./Nav-hov";
import { usePathname } from "next/navigation";
import { useEffect } from "react";
import { Turret_Road } from "next/font/google";
const turrant=Turret_Road({

  weight: '500',
  subsets:['latin'],

})
export default function Navbar() {
  let pathname = usePathname();

  useEffect(() => {}, [pathname]);

  return (
    <>
      <div className="text-white min-w-sreen  bg-navCor   flex justify-center fixed w-full z-10 ">
        <div className="flex justify-center  max-w-[1440px] w-[1440px]   ">
          <nav
            className="height-nav max-[500px]:px-5 min-[500px]:px-[80px] flex  items-center justify-between   lg:max-w-[1440px] w-full z-10 h-[90px] max-sm:h-[79px] "
            aria-label="Global"
          >
            <div className="flex lg:flex-1 text-white flex-row gap-3 ">
              <span className="-m-1.5 p-1.5 flex items-center">
                <Link href="/">
                  <Image
                    src={logo}
                    alt="Tok"
                    width={32}
                    height={40}
                    className="rounded-full lg:h-[50px] lg:w-[50px] "
                    quality={100}
                  />
                  
                </Link>
              </span>
              <span className="flex items-center h-[49px] w-[85px] text-xl bg-gradient-to-r from-pink-500 to-purple-500 text-transparent bg-clip-text font-bold">
                <Link href="/" className={`${turrant.className} text-[32px] max-lg:text-[20px]`} >Occo</Link>
              </span>
            </div>
            <div className="flex lg:hidden flex-row gap-5 items-center   ">
              <div className="h-[90px] w-full  flex items-center max-[205px]:hidden">
                <button className="bg-gradient-to-r from-p_1 to-p_2 text-white font-semibold rounded-full p-[1.5px]  w-full min-w-[110px] h-[36px] ">
                  <span
                    className="flex w-full justify-center bg-navCor text-white rounded-full p-2 px-5"
                    style={{
                      backgroundImage:
                        pathname == "/upgrade"
                          ? "linear-gradient(to right bottom, #6603AC, #EF01BC )"
                          : "",
                    }}
                  >
                    <Link href={ROUTES.PAGE.UPGRADE} className="text-[16px] max-lg:text-[10px]"> Nâng cấp VIP</Link>
                  </span>
                </button>
              </div>
              <button
                type="button"
                className="-m-2.5 inline-flex items-center justify-center rounded-md p-2.5 text-white-700 dropdown"
              >
                <span>
                  <NavHov />
                </span>
              </button>
            </div>
            <div className="flex flex-row gap-5 max-[1300px]:gap-0 items-center  max-lg:hidden text-customGrey">
              <NavOption />
            </div>
          </nav>
        </div>
      </div>
    </>
  );
}
