import { Content } from "@/utils";
export default function PrivacyOcco() {
  return (
    <>
        <div className="py-5 min-h-screen text-white flex justify-center flex flex-col overflow-x-scroll no-scrollbar ">
        <div className="flex justify-center">
        <div className="flex justify-center py-10   text-white max-w-[1440px] max-sm:text-[14px]  lg:text-[18px] sm:text-[16px] max-sm:text-[14px] max-[500px]:px-5 min-[500px]:px-[80px] duration-100">
          {Content.privacy.title}
        </div>
        </div>
        <div className="flex justify-center">
          <div className="max-w-[1440px]  text-white  max-[500px]:px-5 min-[500px]:px-[80px]  lg:text-[18px] sm:text-[16px] max-sm:text-[14px]">
          {Content.privacy.privacy.map((item, index) => {
            return (
              <>
                <div key={index} className=" max-sm:text-[14px] sm:text-[16px] lg:text-[18px] duration-100"><b>{item.title}</b></div>
                <div key={index} style={{ marginTop: '8px'}} className=" max-sm:text-[14px] sm:text-[16px] lg:text-[18px] duration-100"><b>{item.title_1}</b></div>
                
                {item?.des.map((item) => {
                  return (
                    <>
                    <div key={item} dangerouslySetInnerHTML={{ __html: item }} style={{ paddingLeft: '15px', paddingTop: '10px' }} className=" py-3    max-sm:text-[14px] lg:text-[18px] max-sm:text-[14px] sm:text-[16px] lg:text-[18px] leading-[30px] max-sm:leading-[22px] duration-100" />
                      {/* <div key={item} style={{ paddingLeft: '15px' }} className=" py-3    max-sm:text-[14px] lg:text-[18px] max-sm:text-[14px] sm:text-[16px] lg:text-[18px] leading-[30px] max-sm:leading-[22px] duration-100">{item}</div> */}
                    </>
                  );
                })}
              </>
            );
          })}
          </div>
        </div>

        <div style={{ paddingTop: 'inherit' }} className="flex justify-center pt- text-center max-sm:text-sm max-[500px]:px-5 min-[500px]:px-[80px] lg:text-[18px] sm:text-[16px] max-sm:text-[14px]">
          {/* {Content.rule.conclusion} */}
        </div>
      </div>

    </>
  );
}
      