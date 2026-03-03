---
title: "Renaissance Technologies"
date: 2020-09-15T14:38:30+01:00
lastmod: 2026-03-03T14:38:30+01:00
---

![Renaissance Technologies](rentec-aerial-view.png)

After reading [Gregory Zuckerman&rsquo;s](https://www.gregoryzuckerman.com) [The Man Who Solved the Market: How Jim Simons Launched the Quant Revolution](https://www.amazon.com/Man-Who-Solved-Market-Revolution/dp/073521798X) I wanted to find out more about [Renaissance Technologies](https://www.rentec.com/) (RenTec). There are a lot of interviews with Jim Simons and other videos related to Renaissance/Medallion on YouTube but I could not find anything that doesn&rsquo;t just echo what&rsquo;s in the book. I thought it might be more interesting to hear from other people working at the company. Below is what I was able to find.

I also made a short [video](https://www.youtube.com/watch?v=EPdKS7BZ7M8) that contains the interesting parts from the videos I was able to find.

## David Magerman

[David Magerman](http://www-cs-students.stanford.edu/~magerman/) was deeply involved in building RenTec&rsquo;s trading systems beginning in the mid-1990s. I found two videos on YouTube in which he talks about some of the technical background of the company and offers interesting anecdotes regarding his work there. Keep in mind that some of the information could be outdated since Magerman left the company in May 2017.

In the [first video](https://youtu.be/_mu2LbPIhR4?start=772&end=823) (relevant part 12:53-13:43) he gives an example of how important it is to not use unnecessarily complex solutions by explaining that instead of a database they used human-readable ASCII files as a storage format:

> “This design was so useful, for so many other reasons, we never found the value in switching to a more complex database storage format. Years and years later, we continue to reap the benefits of that simple solution and thank the engineering gods that we never moved away from it.”
>
> — David Magerman

Looking at current (September 2020) [job openings](https://www.rentec.com/Careers.action) shows that all roles related directly to trading do not mention any database software; the company is looking for researchers/programmers with “expert level knowledge of C/C++/C++11 and programming tools in a Linux/Unix environment”. The only job role that mentions a database (PostgreSQL) is related to fund administration ("post-trade activities including fund accounting, risk reporting", and more).

In the [second video](https://youtu.be/pWu7mzV9S7Y?start=849&end=1354) (relevant part 14:09-22:34) he talks about what he learned at Renaissance and the company&rsquo;s approach to trading:

### Renaissance operates like a Casino

The company&rsquo;s researchers look for a small edge and then generate returns through the law of large numbers (LLN). They also used leverage (4x-7x) because that allowed them to arrive at the LLN quicker.

### News/fundamental information

They knew they could not analyze all the news for thousands of stocks. But they knew that there were people—experts on stocks—who were doing the analysis, following the news and betting based on that. So by just looking at stock prices Renaissance could glean what they needed to know about stocks.

E.g., Renaissance looked at stocks that were going up a lot based on over-betting. They looked for what they called “reversionary signals”, e.g., stock going up too much relative to its industry. Then they would short that stock.

The core lesson they learned is: information/news is not what you think it is. In the example above good news for a stock signal that the stock is going to fall.

Magerman&rsquo;s advice is to not try to get ahead by using information like news because there will always be bigger fish being faster at that. Instead, think about other investors&rsquo; psychology and reverse-engineer what they are doing.

### What determines stock prices

The company almost failed in 2008 when they lost over 1 billion USD per day for a week. Another quant fund that was going out of business was covering huge short positions (which it had used to hedge long positions), pushing prices higher. A lot of other funds including Renaissance used the same (“boring technology”) stocks to hedge long positions. As a result, everybody started losing money as the closing fund pushed prices higher.

Why did they use “boring” technology stocks: because they rise and fall in tandem with their industry. Industry goes up 10%, IBM goes up 10%. This is what they want: low, predictable volatility.

At another point in the video he also mentions, e.g., that they were “... holding from a day, to a week, to a month, but, you know, usually on the shorter side.”

## Nick Patterson

[Nick Patterson](https://en.wikipedia.org/wiki/Nick_Patterson_%28scientist%29) joined RenTec in the early 1990s and was initially highly skeptical of the company&rsquo;s success.

The following three passages are from [“AI Safety and The Legacy of Bletchley Park”](http://www.thetalkingmachines.com/episodes/ai-safety-and-legacy-bletchley-park), an episode of the podcast _[Talking Machines](http://www.thetalkingmachines.com)_.

> 30:06 [...] I joined a hedged fund, Renaissance Technologies, I&rsquo;ll make a comment about that. It&rsquo;s funny that I think the most important thing to do on data analysis is to do the simple things right. So, here&rsquo;s a kind of non-secret about what we did at renaissance: in my opinion, our most important statistical tool was simple regression with one target and one independent variable. It&rsquo;s the simplest statistical model you can imagine. Any reasonably smart high school student could do it. Now we have some of the smartest people around, working in our hedge fund, we have string theorists we recruited from Harvard, and they&rsquo;re doing simple regression. Is this stupid and pointless? Should we be hiring stupider people and paying them less? And the answer is no. And the reason is nobody tells you what the variables you should be regressing [are]. What&rsquo;s the target. Should you do a nonlinear transform before you regress? What&rsquo;s the source? Should you clean your data? Do you notice when your results are obviously rubbish? And so on. And the smarter you are the less likely you are to make a stupid mistake. And that&rsquo;s why I think you often need smart people who appear to be doing something technically very easy, but actually usually not so easy.
>
> 38:03 [...] my hedge fund, which was not a very big company, we had 7 Phd&rsquo;s just cleaning data and organizing the databases.
>
> 38:22 If any of your listeners are thinking that they can play the market by modeling financial data, the first thing I&rsquo;ll tell them is the data you can buy will be full of trash.

## Peter Brown (CEO)

The senate hearing ["Abuse of Structured Financial Products: Misusing Basket Options to Avoid Taxes and Leverage Limits"](https://www.hsgac.senate.gov/subcommittees/investigations/hearings/abuse-of-structured-financial-products_misusing-basket-options-to-avoid-taxes-and-leverage-limits) ([transcript](https://www.govinfo.gov/content/pkg/CHRG-113shrg89882/html/CHRG-113shrg89882.htm), [PDF](https://www.hsgac.senate.gov/imo/media/doc/REPORT-Abuse%20of%20Structured%20Financial%20Products%20%28Basket%20Options%29%20%287-22-14,%20updated%209-30-14%29.pdf), [video](https://www.hsgac.senate.gov/templates/watch.cfm?id=21130710-5056-A032-52C9-EFE80126EF42)) on Renaissance&rsquo;s basket options trading was also a source referenced in Zuckerman&rsquo;s book. The company&rsquo;s CEO Peter Brown answers Sen. Carl Levin&rsquo;s questions starting at 4:55:30:

> Senator Levin. And how many employees are there at RenTec?
>
> Mr. Brown. I think roughly 300.
>
> Senator Levin. And of these employees, how many work part-
> time or full-time on the algorithm strategy that supports or
> supported RenTec&rsquo;s basket option transaction?
>
> Mr. Brown. Well, on the strategy, 50 or so.
>
> Senator Levin. OK. And these would be employees with
> backgrounds in mathematics, physics, and computer science?
>
> Mr. Brown. That is correct.
>
> Senator Levin. The employees that worked on the overall
> strategy to identify market inefficiencies in order to take
> advantage of them I assume did this on an ongoing basis. is
> that correct?
>
> Mr. Brown. Yes.
>
> Senator Levin. And how frequently were they identifying
> these inefficiencies and modifying the inputs that go into the
> overall strategy? Was that a frequent occasion?
>
> Mr. Brown. Well, most of the modifications involved
> maintenance, changes to--the system has a million lines of
> computer code, and when you have a million lines of computer
> code, it has to be maintained. Interfaces change. I do not know
> if you are counting those kinds of changes.
>
> [...]
>
> Senator Levin. No. How frequently were you doing that? Was
> that a daily change?
>
> Mr. Brown. No.
>
> Senator Levin. Weekly? Monthly?
>
> Mr. Brown. No, more like weekly.
>
> Senator Levin. OK. So every week there would be roughly?
>
> Mr. Brown. One or two changes, roughly, on average.
>
> Senator Levin. In the algorithm?
>
> Mr. Brown. Yes. The algorithm has been developed over 25
> years. It probably has a thousand man-years of work into it. It
> is very mature at this point. It is very hard to make
> significant improvements. So these are minor changes typically.
>
> [...]
>
> Senator Levin. Now, you have about 300,000 transactions
> executed in the banks per day for RenTec&rsquo;s basket contracts.
> Were these submitted in the form of recommendations or
> suggestions to the banks?
> Assuming they met the guidelines, of course, which you had
> already agreed upon. But were these submitted, 300,000,
> approximately, transactions in the banks each day for the
> basket of contracts, were they submitted in the form of
> recommendations or suggestions, but were they automatically
> sent to the market providing they met the guidelines which you
> had agreed to?
>
> Mr. Brown. So they were most commonly sent to the banks&rsquo;
> trading systems.
>
> Senator Levin. All right.
>
> Mr. Brown. And if they--sometimes they were rejected. Not
> very often. And, otherwise, they went to the market. That is
> correct.
>
> Senator Levin. And not very often would mean if they did
> not meet the guideline?
>
> Mr. Brown. I think that is the only--the only ones I know
> of where, you know, the restricted list had been changed and we
> were not aware of it, that kind of thing. Those are the ones I
> know of.
>
> Senator Levin. All right. So there was an agreement, there
> were guidelines, a restricted list, whatever you want to call
> it. If it did not meet that, then it would not go to market.
>
> Mr. Brown. That is my understanding, yes.
>
> Senator Levin. And that did not happen very often.
>
> Mr. Brown. No, it did not.
>
> Senator Levin. How many times?
>
> Mr. Brown. I do not know how many times----
>
> Senator Levin. How many times in a year?
>
> Mr. Brown. A few.
>
> Senator Levin. A few in a year.
>
> Mr. Brown. I would guess. You know, I am not----
>
> Senator Levin. I know.
>
> Mr. Brown. I am guessing there.
>
> Senator Levin. To the best of your ability, you are
> guessing a few times a year?
>
> Mr. Brown. Yes. I mean, you know, if it is 20, it would not
> surprise me. If it is three, it would not surprise me. In that
> range.
>
> Senator Levin. All right. That is out of 30 million a year.
>
> Mr. Brown. I have not done the multiplication, but that is
> probably correct.
>
> Senator Levin. That is not multiplication. That is a
> question of fact.
>
> Mr. Brown. Well, I do not know if it is 30 million or 35
> million or 40 million. It is millions, many millions.
>
> Senator Levin. Tens of millions.
>
> Mr. Brown. Yes.
>
> Senator Levin. It could have been three or five or ten
> times it did not meet the guidelines.
>
> Mr. Brown. That is correct.

Brown also gave a [prepared statement](https://www.hsgac.senate.gov/imo/media/doc/STMT%20-%20Renaissance%20%28July%2022%202014%292.pdf) during the hearing:

> We collect all the publicly available data we can find that we believe might bear on the movement of the prices of tradable instruments— news stories, analysts&rsquo; reports, energy reports, crop reports, weather reports, regulatory filings, accounting data, and, of course, quotes and trades from markets around the world. Our models use this data to make predictions about future price changes. [...]
>
> The model developed by Renaissance for Medallion makes predictions that are profitable only slightly more often than not. Moreover, the predicted price movements can be easily overwhelmed by external events. To compensate for these factors, the model generates a large number of recommendations, so that by virtue of the mathematical principle known as the law of large numbers, the variability of the returns produced by the model is greatly reduced.
>
> However, because the model&rsquo;s recommendations are expected to be profitable only slightly more often than not, the rate of return obtained by applying the recommendations to an unleveraged portfolio would be very small. Leverage magnifies the effect of positive changes in the overall value of the portfolio on the rate of return, and this effect is greater the higher the level of leverage employed.

## Post on Quora

[This](https://www.quora.com/What-are-the-investment-strategies-of-James-Simons-Renaissance-Technologies-I-understand-he-employs-complex-mathematical-models-along-with-statistical-analyses-to-predict-non-equilibrium-changes/answer/James-Baker-69?ch=15&oid=15556100&share=00bcc844&target_type=answer) post on Quora elaborates a bit on what Nick Patterson said—that RenTec is not using more advanced models or techniques than other funds. It also references the 2014 Senate hearing mentioned above.

> There are millions of details, and they are essential to the performance.
> [...]
> The core strategy is portfolio-level statistical arbitrage carried to the limit and executed extremely well. Basically, portfolios of long and short positions are created that hedge out market risk, sector risk and any other kind of risk that Renaissance can statistically predict. The extreme degree of hedging reduces that net rate of return but the volatility of the portfolio is reduced by an even greater factor. The standard deviation of the value of the portfolio at a future date is much lower than its expected value. Therefore, with a large number of trades the law of large numbers assures that the probability of a loss is very small. In such a situation, leverage multiplies both the expected return and the volatility by the same multiple, so even with a high leverage the probability of a loss remains very small.
> [...]
> Leverage is needed because, unleveraged, the rate of return of the portfolio is low. However, because the volatility is much less than the expected return there is no limit to how high the leverage could be without increasing the probability of a loss, at least according to the models. Through years of use and refinement, Renaissance knows that its models are very reliable. However, they also know that there is always the risk of something happening that is not covered by the models, in particular something that is outside prior experience, which is called a "Black Swan" event.
> Thus, a call option is ideal: it can provide high leverage and can provide protection both against the very low probability of a loss greater than the option premium and also against the unknown probability of a possibly catastrophic loss due to a Black Swan event.

## Book excerpts

> Chapter Six, p. 109
>
> Berlekamp and others developed a thesis that locals, or floor traders who buy or sell commodities and bonds to keep the market functioning, liked to go home at the end of a trading week holding few or no futures contracts, just in case bad news arose over the weekend that might saddle them with losses. Similarly, brokers on the floors of commodity exchanges seemed to trim futures positions ahead of the economic reports to avoid the possibility that unexpected news might cripple their holdings. These traders got right back into their positions after the weekend, or subsequent to the news releases, helping prices rebound. Medallion’s system would buy when these brokers sold, and sell the investments back to them as they became more comfortable with the risk. “We’re in the insurance business,” Berlekamp told Straus.

Many daytraders also prefer to not hold any stock overnight if the company is in a position to, e.g., dilute existing shareholders. A biotech might release questionable news to push up their stock price and then follow up with a stock offering hours later/during the next pre-market session/two days later.

> Chapter Six, p. 108
>
> Berlekamp also argued that buying and selling infrequently magnifies the consequences of each move. Mess up a couple times, and your portfolio could be doomed. Make a lot of trades, however, and each individual move is less important, reducing a portfolio’s overall risk. [...] If you trade a lot, you only need to be right 51 percent of the time,” Berlekamp argued to a colleague. “We need a smaller edge on each trade.”

While I understand that Renaissance follows a very different approach from someone like Warren Buffett I think it&rsquo;s interesting that both can be highly profitable. Buffett saying you should invest as if you could only make 20 trades in your lifetime, Berlekamp who argued for the opposite. Goes to show how many different ways there are to make (and lose) money in the market, I guess.

> Chapter Six, p. 109
>
> Sifting through Straus’s data, Laufer discovered certain recurring trading sequences based on the day of the week. Monday’s price action often followed Friday’s, for example, while Tuesday saw reversions to earlier trends. [...] The Medallion model began to buy late in the day on a Friday if a clear up-trend existed, for instance, and then sell early Monday, taking advantage of what they called the weekend effect.

Daytraders trading based on news also observe this: Buy on Friday when good news come out, sell on Monday when everyone that heard the news over the weekend wants to buy the stock, pushing it higher.

> Chapter Eight, p. 153
>
> “What you’re really modeling is human behavior,” explains Penavic, the researcher. “Humans are most predictable in times of high stress—they act instinctively and panic. Our entire premise was that human actors will react the way humans did in the past . . . we learned to take advantage.”
>
> Chapter Eleven, p. 199
>
> Simons emphasized several long-held principles. A key one: Scientists and mathematicians need to interact, debate, and share ideas to generate ideal results. Simons’s precept might seem self-evident, but, in some ways, it was radical. Many of Renaissance’s smartest staffers had enjoyed achievement and recognition earlier in their careers toiling away on individual research, rather than teaming with others. Indeed, talented quants can be among the least comfortable working with others. [...] Simons insisted on a different approach—Medallion would have a single, monolithic trading system. All staffers enjoyed full access to each line of the source code underpinning their moneymaking algorithms, all of it readable in cleartext on the firm’s internal network. There would be no corners of the code accessible only to top executives; anyone could make experimental modifications to improve the trading system.
>
> Chapter Eleven, p. 200
>
> Simons created a culture of unusual openness. Staffers wandered into colleagues’ offices offering suggestions and initiating collaborations. When they ran into frustrations, the scientists tended to share their work and ask for help, rather than move on to new projects, ensuring that promising ideas weren’t “wasted,” as Simons put it.
>
> Chapter Twelve, p. 221
>
> Soon, researchers were tracking newspaper and newswire stories, internet posts, and more obscure data—such as offshore insurance claims—racing to get their hands on pretty much any information that could be quantified and scrutinized for its predictive value. The Medallion fund became something of a data sponge, soaking up a terabyte, or one trillion bytes, of information annually, buying expensive disk drives and processors to digest, store, and analyze it all, looking for reliable patterns. “There’s no data like more data,” Mercer told a colleague, an expression that became the firm’s hokey mantra.
>
> Chapter Fourteen, p. 272
>
> Driving these reliable gains was a key insight: Stocks and other investments are influenced by more factors and forces than even the most sophisticated investors appreciated. For example, to predict the direction of a stock like Alphabet, the parent of Google, investors generally try to forecast the company’s earnings, the direction of interest rates, the health of the US economy, and the like. Others will anticipate the future of search and online advertising, the outlook for the broader technology industry, the trajectory of global companies, and metrics and ratios related to earnings, book value, and other variables. Renaissance staffers deduced that there is even more that influences investments, including forces not readily apparent or sometimes even logical. By analyzing and estimating hundreds of financial metrics, social media feeds, barometers of online traffic, and pretty much anything that can be quantified and tested, they uncovered new factors, some borderline impossible for most to appreciate. “The inefficiencies are so complex they are, in a sense, hidden in the markets in code,” a staffer says. “RenTec decrypts them. We find them across time, across risk factors, across sectors and industries.” Even more important: Renaissance concluded that there are reliable mathematical relationships between all these forces. Applying data science, the researchers achieved a better sense of when various factors were relevant, how they interrelated, and the frequency with which they influenced shares. They also tested and teased out subtle, nuanced mathematical relationships between various shares—what staffers call multidimensional anomalies—that other investors were oblivious to or didn’t fully understand. “These relationships have to exist, since companies are interconnected in complex ways,” says a former Renaissance executive. “This interconnectedness is hard to model and predict with accuracy, and it changes over time. RenTec has built a machine to model this interconnectedness, track its behavior over time, and bet on when prices seem out of whack according to these models.”
>
> Epilogue, p. 326
>
> Simons shared a few life lessons with the school’s audience: “Work with the smartest people you can, hopefully smarter than you . . . be persistent, don’t give up easily. “Be guided by beauty . . . it can be the way a company runs, or the way an experiment comes out, or the way a theorem comes out, but there’s a sense of beauty when something is working well, almost an aesthetic to it.”
