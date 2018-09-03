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
df<-read.csv("/nfs/kenny/data1/rachee/multicdn/processed_data/per_src_ctn_pfx_counts.csv",
	header=TRUE)
df$date <- as.POSIXct(df$ts, origin="1970-01-01", tz="UTC")
df<-df[df$ctn %in% c('Europe', 'Asia', 'Africa', 'Oceania', 'North America', 'South America'),]
p <- ggplot(data = df, aes(x=date, y=count, color=ctn)) + geom_point(size=1) + geom_line(size=0.7)
p <- p + xlab("Time") + ylab("Active client prefixes per day") + coord_cartesian(ylim=c(0, 8000))
p <- p + scale_x_datetime(breaks = date_breaks("1 month"))
common_theme(p)
ggsave("generated_plots/msft_v4_active_client.pdf", width=12, height=10, limitsize=F)

df<-read.csv("/nfs/kenny/data1/rachee/multicdn/processed_data/per_dst_ctn_pfx_counts.csv",
	header=TRUE)
df$date <- as.POSIXct(df$ts, origin="1970-01-01", tz="UTC")
df<-df[df$ctn %in% c('Europe', 'Asia', 'Africa', 'Oceania', 'North America', 'South America'),]
p <- ggplot(data = df, aes(x=date, y=count, color=ctn)) + geom_point(size=1) + geom_line(size=0.7)
p <- p + xlab("Time") + ylab("Active server prefixes per day") + coord_cartesian(ylim=c(0, 1500))
p <- p + scale_x_datetime(breaks = date_breaks("1 month"))
common_theme(p)
ggsave("generated_plots/msft_v4_active_dest.pdf", width=12, height=10, limitsize=F)

df<-read.csv("/nfs/kenny/data1/rachee/multicdn/processed_data/per_src_ctn_pfx_counts.csv",
	header=TRUE)
df$date <- as.POSIXct(df$ts, origin="1970-01-01", tz="UTC")
df<-df[df$ctn %in% c('Europe', 'Asia', 'Africa', 'Oceania', 'North America', 'South America'),]
p <- ggplot(data = df, aes(x=date, y=count, color=ctn))  + geom_line(size=1.2)
# p <- p + xlab("Time") + ylab("Active client prefixes per day") 
p <- p + scale_x_datetime(breaks = date_breaks("4 month"), expand=c(0,0)) 
p <- p + scale_y_log10(limits=c(1, 8000), breaks=c(1, 10, 100, 1000, 6000), expand=c(0,0))
common_theme(p) + guides(colour = guide_legend(nrow =2)) +
theme(legend.justification = c(1, 0), legend.position = c(0.95, 0.2)) + 
xlab("Time") + ylab("Active client prefixes\n per day") 	
ggsave("generated_plots/msft_v4_active_client_log.pdf", width=8, height=6, limitsize=F)

df<-read.csv("/nfs/kenny/data1/rachee/multicdn/processed_data/per_dst_ctn_pfx_counts.csv",
	header=TRUE)
df<-df[df$ctn %in% c('Europe', 'Asia', 'Africa', 'Oceania', 'North America', 'South America'),]
df$date <- as.POSIXct(df$ts, origin="1970-01-01", tz="UTC")
p <- ggplot(data = df, aes(x=date, y=count, color=ctn)) + geom_line(size=1.2)
# p <- p + xlab("Time") + ylab("Active server prefixes per day") 
p <- p + scale_x_datetime(breaks = date_breaks("4 month"), expand=c(0,0))
p <- p + scale_y_log10(limits=c(1, 2000), breaks=c(1, 10, 100, 1000, 2000), expand=c(0,0))
common_theme(p) + guides(colour = guide_legend(nrow =2)) +
theme(legend.justification = c(1, 0), legend.position = c(0.95, 0.2)) +
xlab("Time") + ylab("Active server prefixes\n per day") 
ggsave("generated_plots/msft_v4_active_dest_log.pdf", width=8, height=6, limitsize=F)
