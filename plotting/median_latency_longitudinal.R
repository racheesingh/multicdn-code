library(grid)
library("scales")
library(ggplot2)
common_theme <- function(p) {
  p <- p + theme_minimal()
  p <- p + theme(title=element_text(size=25), text=element_text(size=25))
  p <- p + theme(axis.ticks=element_blank(), axis.ticks.length=unit(0,"mm"),
    plot.margin = unit(c(1,1,1,1), "cm"),
    legend.position="top", axis.text=element_text(margin=unit(0.5,"mm")))
  p<-p + theme( axis.text.x = element_text(angle = 60,
       	 	# vjust=hjust = 0.3,
		margin = margin(t=50, l=20),
		color="black"),
                axis.text.y=element_text(color="black"),
		legend.title = element_blank(),
		panel.border = element_rect(fill=NA,color="black", size=0.3,
		                                    linetype="solid"))
		
  p
}

options(scipen=10000)
df<-read.csv("/nfs/kenny/data1/rachee/multicdn/processed_data/per_day_median_msft_v4.csv",
	header=TRUE)
df$date <- as.POSIXct(df$ts, origin="1970-01-01", tz="UTC")
shade_x_min <- as.POSIXct(sprintf("%s", '2017-01-01'), format="%Y-%m-%d", origin="1970-01-01")
shade_x_max <- as.POSIXct(sprintf("%s", '2017-02-01'), format="%Y-%m-%d", origin="1970-01-01")
df<-df[df$ctn %in% c('Europe', 'Asia', 'Africa', 'Oceania', 'North America', 'South America'),]
p <- ggplot(data = df, aes(x=date, y=rtt, color=ctn)) + geom_line(size=1)
p <- p + xlab("Time") + ylab("Median RTT ")
p <- p + scale_x_datetime(breaks = date_breaks("2 month"))
common_theme(p)
ggsave("generated_plots/msft_v4_median_latency.png", width=16, height=10)

