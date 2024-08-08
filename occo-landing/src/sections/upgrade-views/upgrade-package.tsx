import { Content } from "@/utils";

export default function UpgradePackage() {
  return (
    <>
      <div className="py-5  text-white   max-[500px]:px-5 min-[500px]:px-[80px]">
       <div className="flex justify-center   place-items-start">
        <div className="max-w-[1440px]">
        <div className="flex justify-center text-center flex-col gap-y-5 pb-5">
          <div className=" font-bold lg:text-[50px] max-sm:text-[22px]">{Content.upgrade.register}</div>
          <div className="flex justify-center"><div className=" text-customGrey text-lg w-[713px] h-[73px]  max-sm:w-[353px] max-sm:h-[65px] max-sm:text-[14px] max-[909px]:w-[550px]">{Content.upgrade.re_des}</div></div>
        </div>
        <div className="py-5 grid grid-cols-3  gap-5 max-sm:gap-2 max-sm:px-0 max-[8px]:gap-5 max-[8px]:px-5 max-[355px]:gap-5  w-full px-5">
          {Content.upgrade.card &&
            Content.upgrade.card.map((item,index) => {
              return (
                <>
                  <div
                  key={index}
                    className="package flex  h-[517px] bg-customBlack rounded-2xl relative flex-col border-2
                     border-purple-600 min-h-max  w-[412px]  max-sm:w-[108px]  max-sm:h-[163px]  
                     max-lg:h-[250px] max-lg:w-[240px] max750px]:w-[150px]  max-[1410px]:w-[250px] 
                     max-[910px]:w-[210px] max-[790px]:w-[170px]  duration-100"
                    style={{
                      borderColor:
                        "linear-gradient(to bottom, #EF01BC 0%,#6603AC 100%)",
                    }}
                  >
                    <div className="flex justify-center">
                      <div
                        className="  absolute  top-[-19px] max-[760px]:top-[-15px] max-sm:top-[-10px] 
                        rounded-xl px-1 py-2 w-[200px] text-center font-semibold text-[20px] max-sm:w-[64px] 
                        max-sm:text-[7px] max-sm:h-[18px] max-[1410px]:text-[15px] flex items-center justify-center
                         max-[900px]:w-[150px]  max-[790px]:w-[90px]   max-[790px]:text-[10px]  
                         max-[750px]:text-[8px]  max-[120px]:w-[90px] max-[1302px]:w-[130px] "
                        style={{ backgroundColor: "#FF6539" }}
                      >
                        {item.title}
                      </div>
                    </div>
                    <div className="lg:mt-10 gap-y-5 max-lg:mt-5 max-sm:mt-[3px]">
                      <div className="flex justify-center  font-bold lg:text-[110px] max-sm:text-[30px] max-lg:text-[30px]" >
                        {item.month}
                      </div>
                      <div
                        className="flex justify-center text-2xl font-semibold	text-purple-500  font-semibold lg:text-[48px] max-sm:text-[16px]"
                        style={{ color: "#A11BC7" }}
                      >
                        Tháng
                      </div>
                      <div className="flex justify-center text-xl font-bold lg:pt-10 lg:text-[50px] max-sm:text-[16px] py-1" >
                        {item.price} Thóc
                      </div>
                      <div className="flex justify-center lg:pt-10 text-sm w-[100%] text-center lg:text-[30px]    max-sm:text-[10px]  max-[1302px]:text-[25px] max-sm:leading-0 max-sm:px-0 max-[660px]:leading-3   min-[660px]:leading-8  max-[1301px]:px-5 max-[1301px]:leading-8 max-[660px]:px-0 max-[790px]:text-[14px] min-[640px]:py-2 min-[1029px]:px-2  "  >
                        {`${item.price}.000`}  <span></span>đ/Tháng
                      </div>
                      <div className="flex justify-center lg:py-5 max-lg:py-2">
                        <button
                          className="bg-red-900 w-[80%] rounded-full max-sm:w-[68px] max-sm:h-[18px] flex items-center justify-center "
                          style={{
                            backgroundImage:
                              "linear-gradient(to right bottom, #6603AC, #EF01BC )",
                            borderImageSlice: 1,
                          }}
                        >
                          <div className="max-sm:text-[8px] font-bold py-[10px]" >Mua</div>
                        </button>
                      </div>
                    </div>
                  </div>
                </>
              );
            })}
        </div>
        </div>
      
       </div>
      </div>
    </>
  );
}
