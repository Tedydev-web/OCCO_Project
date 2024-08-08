import group from "../../../public/asset/images/bgload.png";
import Image from "next/image";
import qr1 from "../../../public/asset/images/qr1.png";
import qr2 from "../../../public/asset/images/qr2.png";
import blackAppStore from "../../../public/asset/images/Group (1).png";
import google from "../../../public/asset/images/google_play.png";
import { Content } from "@/utils";
import email from "../../../public/asset/images/email.png";
import iconPhone from "../../../public/asset/images/icon_phone.png";
import location from "../../../public/asset/images/location.png";
import mail from "../../../public/asset/images/mail.png";
import Link from "next/link";

export default function LandingFooter() {
  return (
    <>
      <div className="flex  2xl:text-2xl flex-col pt-15 py-5  min-w-screen text-white justify-center relative min-[787px]:hidden  lg:max-h-[30vh] w-full z-0 ">
        <div className="flex flex-col py-5 ">
          <div className="w-full flex max-[500px]:px-5 min-[500px]:px-[80px] ">
          <div className="text-2xl font-bold  lg:text-5xl max-sm:text-[22px] flex max-sm:w-[320px]    text-lg max-sm:text-[14px] h-fit w-[540px] w-fit">
            {Content.HomeContent.registerContact}
          </div>
          </div>
          <div className="flex max-[500px]:px-5 min-[500px]:px-[80px] ">
          <div
            className="py-3 max-sm:w-[390px] max-sm:min-h-[48px] t   text-lg max-sm:text-[14px] h-full  min-h-[48px]  w-[540px]"
            style={{ color: "#817DA0" }}
          >
            {Content.HomeContent.contact_des}
          </div>
          </div>
          <div className="  flex gap-2    lg:justify-between flex max-[500px]:px-5 min-[500px]:px-[80px]  ">
            <div className=" bg-customBlack border-b border-b-customGrey flex items-center  ">
              <input
                placeholder="Email của bạn"
                className="border-0 bg-customBlack w-full max-sm:max-w-[280px] focus:outline-none  max-[1024px]:w-[500px] "
              />
            </div>

            <Image src={email} height={34} width={34} alt="" className="" />
          </div>
        </div>
        <div className="max-h-[650px]">
          <div className=" flex justify-center z-0">
            <Image src={group} width={313} height={389} alt="" />
          </div>
          <div className=" flex justify-center relative bottom-[180px] max-[500px]:px-5 min-[500px]:px-[40px] ">
            <div className="bg-gradient-to-r from-purple_cus to-blue_pur max-[500px]:w-full  w-[360px] h-[400px]  z-10 rounded-3xl ">
              <div className="py-10 px-5 flex flex-col">
                <div className="font-bold text-2xl">
                  <div>Tải xuống ứng dụng để</div>
                  <div>kết bạn, tương tác</div>
                  <div> chia sẻ, giải trí</div>
                </div>
                <div className="py-5 flex flex-row gap-5">
                  <div className="">
                    <Image src={qr1} width={70} height={70} alt="" />
                    <div className="pt-3">App Store</div>
                  </div>
                  <div>
                    <Image src={qr1} width={70} height={70} alt="" />
                    <div className="pt-3">Google Play</div>
                  </div>
                </div>
                <div>
                  <div className="font-bold text-md w-[300px]">
                    Tải xuống ứng dụng ngay bây giờ để trải nghiệm
                  </div>
                  <div className="flex flex-row gap-5 pt-3">
                    <div>
                      <button className=" w-[104px] h-[33px] ">
                        <Link href="https://www.apple.com/vn/app-store/">
                          {" "}
                          <Image src={blackAppStore} alt="" quality={100} />
                        </Link>
                      </button>
                    </div>
                    <div>
                      <button className=" w-[104px] h-[33px] ">
                        <Link href="https://play.google.com/store/apps/details?id=com.ea.game.pvzfree_row&hl=vi">
                          {" "}
                          <Image src={google} alt="" quality={100} />
                        </Link>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="flex justify-center w-min-screen w-max-screen lg:mt-20  max-h-[580px]  min-[500px]:px-[80px] z-0  ">
        <div className="pt-10  max-w-[1440px] text-white max-[787px]:hidden overflow-hidden">
          <div className="grid grid-cols-2">
            <div className="col-span-1 row-span-2">
              {" "}
              <div className=" flex justify-center z-0">
                <Image src={group} width={313} height={389} alt="" />
              </div>
            </div>
            <div className="col-span-1 row-span-1 ">
              {" "}
              <div className="flex flex-col py-5 ">
                <div className="text-2xl font-bold">
                  {Content.HomeContent.registerContact}
                </div>
                <div
                  className="py-3 max-sm:w-[320px] max-sm:h-[48px] text-sm "
                  style={{ color: "#817DA0" }}
                >
                  {Content.HomeContent.contact_des}
                </div>
                <div className="  flex gap-5 py-3 max-sm:justify-between  overflow-hidden">
                  <div className=" bg-customBlack border-b border-b-customGrey flex items-center lg:w-[80%] z-0  ">
                    <input
                      placeholder="Email của bạn"
                      className="border-0 bg-customBlack max-sm:w-[270px] focus:outline-none"
                    />
                  </div>

                  <Image
                    src={email}
                    height={34}
                    width={34}
                    alt=""
                    className="relative left-[3%]"
                    quality={100}
                  />
                </div>
              </div>
            </div>
            <div className="col-span-2 row-span-2  ">
              <div className=" flex justify-center relative top-[-170px] ">
                <div className="bg-gradient-to-r from-purple_cus to-blue_pur   w-full max-w-[1440px]  z-0 rounded-3xl   h-[255px] flex items-center px-8">
                  <div className="  flex flex-row items-center justify-center gap-10 px-5 ">
                    <div className="font-bold w-[379px] h-[144px] text-[34px] max-[1350px]:text-[27px] max-[1110px]:text-[25px] max-[900px]:text-[22px] max-[730px]:text-[20px] duration-100">
                      <div>
                        Tải xuống ứng dụng để kết bạn, tương tác, chia sẻ, giải trí
                      </div>
                    </div>
                    <div className="py-5 flex flex-row gap-7   max-[800px]:gap-3">
                      <div className="">
                        <Image src={qr1} width={109} height={109} alt="" />
                        <div className="pt-3 w-full text-center text-[18px]  max-[1493px]:text-[16px] max-[1075px]:text-[8px] max-[1360px]:text-[10px]">
                          App Store
                        </div>
                      </div>
                      <div>
                        <Image src={qr1} width={109} height={109} alt="" />
                        <div className="pt-3 w-full text-center text-[18px]  max-[1493px]:text-[16px]  max-[1075px]:text-[8px] max-[1360px]:text-[10px]">
                          Google Play
                        </div>
                      </div>
                    </div>
                    <div>
                      <div
                        className="font-medium text-[24px] max-[900px]:text-[16px] duration-100"
                       
                      >
                        Tải xuống ứng dụng ngay bây giờ để trải nghiệm
                      </div>
                      <div className="flex flex-row gap-5 pt-3">
                        <div className="    ">
                          <button>
                            <Link
                              href="https://www.apple.com/vn/app-store/"
                              className="    "
                            >
                              <Image
                                src={blackAppStore}
                                alt=""
                                quality={100}
                                width={153}
                                height={50}
                              />{" "}
                            </Link>
                          </button>
                        </div>
                        <div>
                          <button>
                            <Link
                              href="https://play.google.com/store/games?device=windows&utm_source=apac_med&hl=vi-VN&utm_medium=hasem&utm_content=Jan0324&utm_campaign=Evergreen&pcampaignid=MKT-EDR-apac-vn-1707570-med-hasem-py-Evergreen-Jan0324-Text_Search_BKWS-BKWS%7CONSEM_kwid_43700064211720884_creativeid_525822890288_device_c&gad_source=1&gclid=CjwKCAjw1K-zBhBIEiwAWeCOF9xvAjiIM0cW0NjgKDhBiqzQhfov6hivOmbkMCe1plc7draQyMwdYhoCZX0QAvD_BwE&gclsrc=aw.ds"
                              className="    "
                            >
                              {" "}
                              <Image
                                src={google}
                                alt=""
                                quality={100}
                                width={153}
                                height={50}
                              />
                            </Link>
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
               
                </div>

                <br />
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
