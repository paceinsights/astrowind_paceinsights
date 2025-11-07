---
publishDate: 2025-11-07T00:00:00Z
title: "What I Learned Building a RAG System Over the Last Year"
excerpt: "A year of building an AI knowledge assistant taught me something unexpected: the game-changing shift isn't what AI can build—it's how fast you can now experiment with different approaches."
category: "AI Development"
tags:
  - ai
  - rag systems
  - rapid development
  - experimentation
  - software development
image: ~/assets/images/PaceInsights_AI_Strategy.png
author: "Samir Abid"
metadata:
  canonical: https://paceinsights.com/articles/what-i-learned-building-rag-system
---

I've been building an AI knowledge assistant for about a year now. You know the type - feed it all your company documents and it becomes this expert chatbot that can answer questions about anything you've ever written down.

When I started, I thought the hard part would be making the AI accurate. Getting it to understand context properly. Making sure it didn't just make things up.

And yeah, those things were hard.

But what I actually learned - what genuinely surprised me - was something different. It was about how fast you can try things now. And what that changes about building software.

Let me walk you through what happened.

## Starting Point

I did what everyone does first. Set up a vector database. That's the standard approach for this kind of system.

The way it works: you take your PDFs, break them into chunks, turn them into these mathematical representations, store them in a database. Someone asks a question, the system finds relevant chunks, sends them to the AI, you get an answer back.

Sometimes this worked really well. Ask about a project and you'd get a solid summary.

Sometimes it didn't work at all. Ask for a specific part number and you'd get... something. Maybe the right thing. Maybe not.

The part number thing bothered me. If I'd just used regular keyword search - you know, literally searching for "1234" - I would've found it instantly.

But I'd switched to "semantic search" which tries to understand meaning rather than just matching words. So it could find documents about specifications, but not always that specific specification.

I spent quite a bit of time trying to tune this. Changing how the system was set up. Different ways of breaking up the documents. Trying to get it more consistent.

We got it working... sort of. But it was hit and miss.

What I found myself doing: you make a choice about how the system works, and you get some things working better, but other things get worse. I kept finding that pattern repeating.

But here's what struck me even then: I was trying all these different approaches in days. Not weeks. Not months. Just trying things, seeing what worked, moving on to the next thing.

## The Hybrid Approach

Then I found out you could combine both methods. Run the semantic search and regular keyword search at the same time, blend the results together.

So now "specification 1234" would get caught by the keyword part. Questions like "how are these projects performing" would get handled by the semantic part.

That helped. A lot, actually. Things got noticeably more consistent.

And again - this took me maybe a few days to implement and test. In the past, this would've been a whole thing. Meetings about whether to try it. Risk assessment. Now I just... tried it.

## The Knowledge Problem

As I added more documents, a new problem showed up.

Ask a question that was mentioned in 50+ documents and the system would try to send all this information to the AI. Too much. The AI would get overwhelmed and give these vague, generic answers.

I discovered you could add what's called a "re-ranker" - basically another AI that looks at all the chunks you found and picks out the most relevant ones before sending them along.

So instead of: find 30 chunks → send to AI, it became: find 30 chunks → re-rank them → keep the best 5 → then send to AI.

This made a big difference in quality.

But it also made everything slower and more expensive. More AI calls, more processing. You find yourself constantly weighing these trade-offs: speed versus quality versus cost.

The thing is, I could test this in under a week. Add the re-ranker, see if it actually helped, measure the difference.

In traditional software development, adding a whole new layer like this would've been a major decision. Architecture reviews. Team discussions about whether it was worth it. Here, I just tried it. It worked. I kept it.

That's when I started noticing the pattern.

## The Graph Database

Eventually I hit a different kind of problem. Context wasn't just living inside documents. It was living between them.

Which projects linked to which clients. Who worked with whom. How things evolved over time.

I'd heard about graph databases - they're like these massive mind maps that can track relationships between things. I looked into Neo4j, which can handle time-based relationships.

The idea was to give all those vector chunks a structure to hang onto. Not just floating content, but content connected to other content in meaningful ways.

This helped too. Another quality improvement.

But here's the bit that made me stop and think: when I looked into implementing this, I got a roadmap from the AI. It said this would take about six weeks.

**We did it in three hours.**

Not because I'm particularly clever. But because the AI could help me write the code, spot the mistakes, suggest better approaches. I stayed focused on the design - what I wanted it to do - and the implementation went way faster than I expected.

That's when it clicked for me. This isn't just about building a better AI system. It's about what happens when you can try things that used to take weeks in a matter of hours.

## What This Actually Changes

Think about how technical decisions normally work.

Someone suggests using a new technology or approach. Management gets nervous. "How long will this take? How much will it cost? How sure are we it'll actually work?"

Developers push back when you want to change direction. "We just spent three weeks implementing this and now you want to change it?"

So you end up being conservative. Sticking with what you know. The political friction alone makes experimentation expensive.

But what if that six-week implementation is actually three hours?

What if trying a completely different approach takes a couple of days instead of a couple of months?

**The risk calculation completely flips.**

You can try things you would've dismissed as too uncertain. The political friction disappears - it's three hours, not three sprints. You can test five different approaches instead of debating which single approach to commit to.

I probably tried more architectural variations in this one year than I would've tried in five years of traditional development. Not because I was smarter about it. Just because I could actually try them.

## What Hasn't Changed

I should be clear - it's not all easy.

Things still break. I still spend days debugging. The AI doesn't get it right every time.

And you're still dealing with the same fundamental trade-offs:
- **Cost**: Every layer you add costs more to run
- **Speed**: Every layer makes the system slower
- **Quality**: That last 10% is still brutally hard to get right

But I can test different solutions to those problems in days instead of months.

Here's a small example: I eventually asked the AI to write its own system prompts. Gave it examples of good answers and poor answers. Let it iterate on improving the prompts.

It actually worked. Measurably better results.

In the past, this would've been a two-week optimization project. Instead it was an afternoon experiment.

That keeps happening. **Things that would've been projects become experiments.**

## What I Think This Means

I set out to build a RAG system. And I did - we've gone from fun prototype to something genuinely useful.

But what I actually learned was about the development process itself.

When I look back at this year, what I've been able to build and test would've taken a team of maybe six people a year to do. Maybe longer. And I think the quality would've been worse, not better.

Because in a team, when you suggest ripping out three weeks of work to try something different, people push back. It gets political. People are tired. The momentum matters.

Here, that friction just... disappeared.

I could stay in design mode - thinking about what I wanted the system to do - rather than spending all my time in the weeds of implementation.

Yes, the AI was involved at every layer. Advising, coding, architecting. But it didn't have to be an AI project specifically. This same pattern would work for building anything.

## The Question That Matters

If you're thinking about AI for your business, I think the question isn't "what can AI do?"

The question is: **"Are we set up to experiment 10x faster than we did last year?"**

Because the biggest advantage isn't what AI builds. It's what AI enables you to try.

The old calculation - "that's too risky, too uncertain, takes too long" - is breaking down.

If your competitors are experimenting at 10x speed and you're not, that gap is going to show up pretty quickly.

I don't have this all figured out. I'm still learning. Still finding limitations and surprises.

But I'm convinced the change isn't really about AI systems. It's about what happens when the cost of trying something new drops by 90%.

That's a different game entirely.

---

Would be great to hear your thoughts and experiences doing this too. [Get in touch](/contact).
