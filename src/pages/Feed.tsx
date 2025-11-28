import { Link } from "react-router-dom"

const newsItems = [
  {
    title: "Tech Giant Unveils Revolutionary AI Assistant",
    description:
      "The new AI assistant promises to redefine personal productivity and digital interaction.",
    image:
      "https://lh3.googleusercontent.com/aida-public/AB6AXuCC9tWBHMVYnovtKGpGsCIHT2zbIANffq0r1kXbOjJ1vOC3F1TwZ5PWSY200ZngdoLQUC7MHcUqXX70-myteJuzv5U9YHujbq2dSFqDXKsPljL16ZThaYH9DVtecDIOeuLQ3wnDQu7Rmp0msem_3JABmfLS99r0VH5hgWmMC_fvAhUt8PmDXZq9itNz80_XotkLnHeAEAXsPs9Nd3G6sun-0RV1rl-M4IFhsJAYwjbOEUilhFbHIkBtdLRfI7YFucumivueEyD_9ig",
    likes: 123,
    comments: 45,
  },
  {
    title: "Climate Change Report: Urgent Action Needed",
    description:
      "A comprehensive report highlights the critical need for immediate and decisive action to combat climate change.",
    image:
      "https://lh3.googleusercontent.com/aida-public/AB6AXuC7MtHt_tVO1rrcObFyH98m4ZJPQH0ocXz7BLoSQwdMraSXxMDRVCw3__kQpViuVIvjLHskQsBz-eabRN0GWghmM9YlbRMLOzsIvjOkGZSgnlC7afZlau3xp4kj-vSSbhTWN6ceYwVZswSwUUHQ3DS6nQs4hfEVpgedS82pgcbz0CNwppjx0S7t0IBGqX2IrxVnAFxvq8cYcJy9hPSphXHn3V4KKaEF86_oZYWRPI9TwiKgMhBgh2X_zLwZ2jOnh0lKRrsGw9Eg-6w",
    likes: 87,
    comments: 22,
  },
  {
    title: "New Study Reveals Benefits of Mindfulness Meditation",
    description:
      "Research indicates that regular mindfulness meditation can significantly reduce stress and improve mental well-being.",
    image:
      "https://lh3.googleusercontent.com/aida-public/AB6AXuCMxIS4Yp0p0TcMwPNgvL36_JQAv2PQ1NBw4sbsLD1tKVcF4IlcexKREIsB6UBgateNaEkkqALCDzPTGa2q86-y5ye_juAf9dPKY24w9nlk-Zxg_efPlRym-hsEeCQsnCTyhPhP_WsRMy3PXuBuEWpkjmEHGRU4BrtQ8rAzTlsZV7L3OgTUi613PyBDCQ15rw81KgxLcOC6zoJ9U2oyMGpDIiB0_S873H_aBW2gW_TLrWVeGafvkSmaFXiVFc1gBBkageBGiVNTb_o",
    likes: 150,
    comments: 60,
  },
  {
    title: "Global Economy Shows Signs of Recovery",
    description:
      "Recent economic data suggests a gradual recovery from the global downturn, with increased consumer spending and business investment.",
    image:
      "https://lh3.googleusercontent.com/aida-public/AB6AXuCPgWdv_oNucekgtg4pPxIlQNRoW8ifaiZ4enz52s43sx89tcXYJXfPC-QBGAQ5BF8iYyYpS40WjG2-0rnKUITnvCnWM8C7d4jf-EMG36uFcBFAYUIlk4ncPLfGNSAI2TlFAHEl8UXRgtkJ3R8Ct2EBYNqXX1buOcxRaQdQLDSaYOTYRaCvmDj1sRzXS90IdpYwivK_NsOzk445XfYzIjKRyVSuztgRL-PoSzxU66M6-dlbZP1u-LqLRE6Nn_jQyKwtcDXKcdAYqMI",
    likes: 95,
    comments: 35,
  },
  {
    title: "Breakthrough in Cancer Research Offers New Hope",
    description:
      "Scientists have made a significant advancement in cancer treatment, potentially leading to more effective therapies.",
    image:
      "https://lh3.googleusercontent.com/aida-public/AB6AXuAXrrjo8eQPqcTh-xvLXxDVVtorj2mpFl4MNfPXSuKGL4e7xgb8aiRttdHsSguNlYyzr6HC-6nGWR3BVnCBQi9SvJwV5IT7Y0FTY9qJnBppkq_6pl-mJUSQhRuK7oVbrX5Fm0Tnge6wOoA4Bt927Ik0soSFRWAySVMreMbvrE8_vMyXsUx5Q8yS_qLrHMYm0LGBYJGMAJgIAAl6AhZObVUfi6e6X-I3V_QuF1ihR8XYZbzxbA01wZJTxId4zCV49QTWxo6rVzlfutI",
    likes: 110,
    comments: 50,
  },
]

export function Feed() {
  return (
    <div className="flex min-h-screen w-full flex-col bg-white dark:bg-black text-black dark:text-white">
      <header className="flex items-center justify-between border-b border-gray-200 dark:border-gray-800 px-4 sm:px-6 lg:px-8 py-3">
        <div className="flex items-center gap-4">
          <Link to="/feed">
            <img src="/logo1.png" alt="Flash News AI logo" className="h-12 w-12 object-contain" />
          </Link>
          <Link to="/" className="text-xl font-bold">
            Flash News AI
          </Link>
        </div>
        <div className="flex items-center gap-4">
          <div className="relative hidden sm:block">
            <svg
              className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-500 dark:text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
            <input
              type="text"
              className="w-full rounded-full border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 py-2 pl-10 pr-4 text-base focus:outline-none focus:ring-2 focus:ring-black dark:focus:ring-white"
              placeholder="Search"
            />
          </div>
          <div
            className="size-10 rounded-full bg-cover bg-center"
            style={{
              backgroundImage:
                'url("https://lh3.googleusercontent.com/aida-public/AB6AXuC7BkXEe6soFk6AQ6s_ClaBC6SbVm5g-y1RsEB-lILPQnTL5re76qPd50H-6aECT4-QgvpnCObUl5WjtSmUaZWpZAQLBQ3wIbJ4ZWGflhU4VCWy2NY1hN6UQlA00JgKbpQCus-b2CvI8xLhF1weyoeDvQCcGjj7KO8V-nUHKu9xzhSTFeR_BQL3oeQuuODAE0vJaUmgTHOiiOeIKlN1QPoRU8lWtYWNV_VmmTSXYTlSFR8vHhORI-m-HXry1L_lkCyJ36T88iKaRDk")',
            }}
          ></div>
        </div>
      </header>
      <main className="flex-1">
        <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
          <h2 className="px-4 text-3xl font-bold">News Feed</h2>
          <div className="mt-6 space-y-8">
            {newsItems.map((item, index) => (
              <div key={index} className="border border-gray-200 dark:border-gray-800 rounded-lg bg-white dark:bg-black">
                <div className="flex flex-col gap-4 p-4 sm:flex-row">
                  <div className="flex flex-1 flex-col gap-3">
                    <div className="space-y-1">
                      <p className="text-lg font-bold">{item.title}</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">{item.description}</p>
                    </div>
                    <Link
                      to="/article"
                      className="inline-flex items-center justify-center gap-2 w-fit px-4 py-2 text-sm font-medium text-white bg-black dark:bg-white dark:text-black rounded-full hover:bg-gray-900 dark:hover:bg-gray-100 transition-colors"
                    >
                      <span>Read More</span>
                      <svg
                        className="h-4 w-4"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M9 5l7 7-7 7"
                        />
                      </svg>
                    </Link>
                  </div>
                  <div
                    className="aspect-video w-full flex-shrink-0 rounded-lg bg-cover bg-center sm:w-64"
                    style={{ backgroundImage: `url("${item.image}")` }}
                  ></div>
                </div>
                <div className="flex items-center gap-4 border-t border-gray-200 dark:border-gray-800 px-4 py-2">
                  <button className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 hover:text-black dark:hover:text-white transition-colors">
                    <svg
                      className="h-5 w-5"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
                      />
                    </svg>
                    <span className="font-semibold">{item.likes}</span>
                  </button>
                  <button className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 hover:text-black dark:hover:text-white transition-colors">
                    <svg
                      className="h-5 w-5"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                      />
                    </svg>
                    <span className="font-semibold">{item.comments}</span>
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  )
}
