/*

MIT License

Copyright (c) 2023 Looker Data Sciences, Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

*/

import React, { useContext, useRef, useEffect } from 'react'
import styled from 'styled-components'
import { LookerEmbedSDK } from '@looker/embed-sdk'
import { ExtensionContext } from '@looker/extension-sdk-react'
import { BardLogo } from './App'

export interface ExploreEmbedProps {
  modelName: string
  exploreName: string
  qid: string
  setExploreLoading: any,
  submit: any
  setSubmit: any
}

/**
 * Renders an embedded Looker explore based on the provided explore URL.
 * @param exploreUrl - The URL of the Looker explore to embed.
 * @param setExplore - A function to set the embedded explore instance.
 * @param submit - boolean for search query
 * @param setSubmit - A function to control the submit behavior of the explore.
 * @returns The ExploreEmbed component.
 */
export const ExploreEmbed = ({
  modelName,
  exploreName,
  qid,
  setExploreLoading,
  submit,
  setSubmit,
}: ExploreEmbedProps) => {
  const { extensionSDK } = useContext(ExtensionContext)
  const [exploreRunStart, setExploreRunStart] = React.useState(false)

  console.log("Explore Embed")

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const canceller = (event: any) => {
    return { cancel: !event.modal }
  }

  const ref = useRef<HTMLDivElement>(null)

  const handleQueryError = () => {
    setTimeout(() => !exploreRunStart && animateExploreLoad(),10)
  }

  const animateExploreLoad = () => {
    console.log("Here")
    setSubmit(false)
    document.getElementById('embedcontainer')?.style.setProperty('opacity', '0.4')
  }

  useEffect(() => {
    const hostUrl = extensionSDK?.lookerHostData?.hostUrl
    const el = ref.current
    if (el && hostUrl && modelName) {
      
      const paramsObj: any = {
        embed_domain: window.origin, //hostUrl,
        qid : `${qid}`,
        toggle: 'dat,pik,vis',
        sdk: '2',
        _theme: JSON.stringify({
          key_color: '#174ea6',
          background_color: '#f4f6fa',
        }),
      }
      
      console.log("=================inside useEffect")  
      console.log(modelName)

      var explore_id = modelName + "::" + exploreName
  
      el.innerHTML = ''
      LookerEmbedSDK.init(hostUrl)
      LookerEmbedSDK.createExploreWithId(explore_id)
        .appendTo(el)
        .withClassName('looker-embed')
        .withParams(paramsObj)
        .on('explore:ready',() => handleQueryError())
        .on('drillmenu:click', canceller)
        .on('drillmodal:explore', canceller)
        .on('explore:run:start', () => {
          setExploreRunStart(true)
          animateExploreLoad()
        })
        .on('explore:run:complete', () => {
          setExploreRunStart(false)
          setSubmit(true)
        })
        .build()
        .connect()
        .then((explore) => {setExploreLoading(explore)
          //console.error('explore in createExploreWithId', explore)
        })
        .catch((error: Error) => {
          // @TODO - This should probably throw a visible error
          // eslint-disable-next-line no-console
          console.error('Connection error', error)
          
        })
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [modelName, exploreName,qid])

  return (
    <>
    <div style={{position:'absolute', display:'flex', flexDirection:'column', alignItems:'center',justifyContent:'center',width:'100%',height:'100%',backgroundColor:'rgb(250, 250, 250,0.1)',zIndex:submit ? 1 : -1}}>
    
    </div>
    <EmbedContainer id="embedcontainer" ref={ref}/>
    </>
  )
}

const EmbedContainer = styled.div`
  backgroundcolor: #f7f7f7;
  height: 100%;
  animation: fadeIn ease-in ease-out 3s;
  > iframe {
    backgroundcolor: #f7f7f7;
    height: 100%;
    width: 100%;
  }
`